from citybot_by_rid.db.data import db_session
from citybot_by_rid.db.data.models import Game
from citybot_by_rid.db.services.user_service import get_user


def create_game(user_id):
    session = db_session.create_session()
    game = Game()
    game.user_id = user_id
    session.add(game)
    session.commit()
    session.close()


def load_game_data(game, data):
    game.is_game_started = data.is_game_started
    game.used_cities = data.used_cities
    game.last_letter = data.last_letter
    game.disappointed = data.disappointed
    return game


def load_game(vk_id):
    user = get_user(vk_id)
    session = db_session.create_session()
    game = session.query(Game).filter(Game.user_id == user.id).first()
    session.close()
    return game


def save_game(game_id, data):
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    game = load_game_data(game, data)
    session.merge(game)
    session.commit()
    session.close()
