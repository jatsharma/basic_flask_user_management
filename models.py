from sqlalchemy import TIMESTAMP, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import inspect


@as_declarative()
class Base:

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def _asdict(self):
        return {
            c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs
        }


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True)
    email = Column(String(30), unique=True)
    username = Column(String(30))
    hashed_password = Column(String)
    country = Column(String(20))
    is_active = Column(Boolean)
    date_created = Column(TIMESTAMP)
    last_updated = Column(TIMESTAMP)