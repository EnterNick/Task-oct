import sqlalchemy
from .db_session import SqlAlchemyBase

import datetime


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    telegram_id = sqlalchemy.Column(sqlalchemy.INTEGER)
    register = sqlalchemy.Column(sqlalchemy.BOOLEAN, default=True)
    inaccuracies = sqlalchemy.Column(sqlalchemy.BOOLEAN, default=True)
    current_save = sqlalchemy.Column(sqlalchemy.String)
    text_1 = sqlalchemy.Column(sqlalchemy.String)
    text_2 = sqlalchemy.Column(sqlalchemy.String)
    text_3 = sqlalchemy.Column(sqlalchemy.String)
    text_4 = sqlalchemy.Column(sqlalchemy.String)
    text_5 = sqlalchemy.Column(sqlalchemy.String)
    text_6 = sqlalchemy.Column(sqlalchemy.String)
    text_7 = sqlalchemy.Column(sqlalchemy.String)
    text_8 = sqlalchemy.Column(sqlalchemy.String)
    text_9 = sqlalchemy.Column(sqlalchemy.String)
    text_10 = sqlalchemy.Column(sqlalchemy.String)
