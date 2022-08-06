from flask import Flask
from flask_restful import Api, Resource, request
from database import registerUser, loginUser, getCurrentActiveUser, engine
from models import Base

app = Flask(__name__)

api = Api(app, prefix="/api")


class UserRegister(Resource):
    def post(self):
        data = request.json
        # Check for required params
        if "email" not in data or "password" not in data or "country" not in data or "username" not in data:
            return {"success": False, "message": "Missing required fields."}, 400
        
        response = registerUser(data)
        return response


class UserLogin(Resource):
    def post(self):
        data = request.json
        # Check for required params
        if "email" not in data or "password" not in data:
            return {"success": False, "message": "Missing required fields."}, 400
        response = loginUser(data)
        return response


class UserInfo(Resource):
    def get(self):
        # Get current user info
        # Get authorization token from headers
        token = request.headers.get("Authorization")
        if token is None:
            return {"success": False, "message": "Session Expired, please login to continue"}, 401
        response = getCurrentActiveUser(token)
        if "success" in response and response["success"] is True:
            del response["user"]["last_updated"]
            del response["user"]["date_created"]
            del response["user"]["id"]
        return response


# ROUTES
api.add_resource(UserRegister, "/register")
api.add_resource(UserLogin, "/login")
api.add_resource(UserInfo, "/user_info")


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    app.run()