from citybot_by_rid.db.data import db_session
from citybot_by_rid.db.data.models import User


def get_user(vk_id):
    session = db_session.create_session()
    user = session.query(User).filter(User.vk_id == vk_id).first()
    session.close()
    return user


def add_user(vk_id):
    session = db_session.create_session()
    user = User()
    user.vk_id = vk_id
    session.add(user)
    session.commit()
    session.close()
