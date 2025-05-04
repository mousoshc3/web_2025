import sqlalchemy
from sqlalchemy_serializer import SerializerMixin


from .db_session import SqlAlchemyBase


# Результат прохождения анкеты
class Questions(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    theme = sqlalchemy.Column(sqlalchemy.String)
    questions = sqlalchemy.Column(sqlalchemy.String)
    short_description = sqlalchemy.Column(sqlalchemy.String)