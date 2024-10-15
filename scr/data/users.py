import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase

import datetime


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    telegram_id = sqlalchemy.Column(sqlalchemy.INTEGER)
    text = sqlalchemy.Column(sqlalchemy.String, default='')
    register = sqlalchemy.Column(sqlalchemy.BOOLEAN, default=True)
    inaccuracies = sqlalchemy.Column(sqlalchemy.BOOLEAN, default=True)
