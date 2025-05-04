import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


from .db_session import SqlAlchemyBase


# Результат прохождения анкеты
class Answers(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'answers'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    answer = sqlalchemy.Column(sqlalchemy.String)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    current_question = sqlalchemy.Column(sqlalchemy.Integer,
                                         default=1)

    completed = sqlalchemy.Column(sqlalchemy.Boolean,
                                  default=False)
    completed_date = sqlalchemy.Column(sqlalchemy.DateTime)
    user = orm.relationship('User')