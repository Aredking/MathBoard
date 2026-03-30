import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class News(SqlAlchemyBase):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'team_leader': self.team_leader,
            'job': self.job,
            'work_size': self.work_size,
            'collaborators': self.collaborators,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'is_finished': self.is_finished
        }
