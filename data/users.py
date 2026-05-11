import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True)
    password = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    register_date = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.func.now())

    characters = sqlalchemy.orm.relationship("Character", back_populates="owner", cascade="all, delete-orphan")