import redis
import os
import random, string
from jose import JWTError, jwt
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
from datetime import timedelta, datetime


from models import Users
from utils import createAccessToken, getPasswordHash, verifyPassword, dbGetUserByEmail

DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(DOTENV_PATH)

DB_URI = os.environ.get("DB_URI")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 10

engine = create_engine(DB_URI, pool_recycle=3600, connect_args={"connect_timeout": 60})
session = sessionmaker(bind=engine)

rclient = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def mk_session(fun):
    # Decorator for db functions
    def wrapper(*args, **kwargs):
        s = session()
        kwargs["session"] = s
        try:
            res = fun(*args, **kwargs)
        except Exception as e:
            s.rollback()
            s.close()
            raise e

        s.close()
        return res
    wrapper.__name__ = fun.__name__
    return wrapper


@mk_session
def registerUser(data, session=None):
    try:
        # Check if user exists, if not then add to DB.
        user_check = dbGetUserByEmail(data["email"], session)
        if user_check:
            return {"success": False, "message": "User with email already exists, please login"}, 400

        hashed_password = getPasswordHash(data["password"])
        now_time = datetime.utcnow()
        # Add user to DB
        new_user = Users(email=data["email"], hashed_password=hashed_password, country=data["country"], \
            is_active=True, date_created=now_time, last_updated=now_time)
        session.add(new_user)
        session.commit()

        return {"success": True, "message": "Register success, please continue to login."}
    except Exception as e:
        print(e)
        return {"success": False, "message": "Something went wrong, please try again."}, 400


@mk_session
def loginUser(data, session=None):
    try:
        user_check = dbGetUserByEmail(data["email"], session)
        if user_check is None:
            return {"success": False, "message": "User with email does not exist, please register."}, 401
        
        if not verifyPassword(data["password"], user_check.hashed_password):
            return {"success": False, "message": "Wrong password, please try again."}, 401

        access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        char_data = "".join(random.sample(string.ascii_letters, 15))
        # Set user email in redis for login checks, for set hours
        rclient.setex(str(char_data), 3600 * ACCESS_TOKEN_EXPIRE_HOURS, user_check.email)
        # Generate access token
        access_token = createAccessToken({"sub": char_data}, expires_delta=access_token_expires)

        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "message": "login successful"
        }
    except Exception as e:
        print(e)
        return {"success": False, "message": "Something went wrong, please try again"}, 400


@mk_session
def getCurrentActiveUser(token, session=None):
    try:
        token = token.split('Bearer ')[1]
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        redis_payload = payload.get("sub")
        email = rclient.get(redis_payload)
        # print("EMAIL: ", email)
        user = dbGetUserByEmail(email, session)
    except JWTError:
        return {"success": False, "message": "Session Expired, please login to continue."}, 401
    if user is None:
        return {"success": False, "message": "Session Expired, please login to continue."}, 401
    if not user.is_active:
        return {"success": False, "message": "Inactive user."}, 400
    user = user._asdict()
    del user['hashed_password']
    return {"success": True, "user": user}