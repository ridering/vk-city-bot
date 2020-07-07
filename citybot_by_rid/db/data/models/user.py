from sqlalchemy import Column, Integer

from citybot_by_rid.db.data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(Integer, nullable=False)
