from sqlalchemy import Column, Integer, Boolean, String, orm, ForeignKey

from citybot_by_rid.db.data.db_session import SqlAlchemyBase


class Game(SqlAlchemyBase):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    is_game_started = Column(Boolean, default=False)
    used_cities = Column(String, nullable=True, default='')
    last_letter = Column(String, nullable=True, default='')
    disappointed = Column(String, nullable=False, default='no')

    user = orm.relation('User', foreign_keys=[user_id])
