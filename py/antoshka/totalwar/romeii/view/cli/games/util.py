from antoshka.totalwar.romeii.games.model import db as games_db


def get_selected_game():
    return games_db.Game.select().order_by(games_db.Game.last_selected.desc()).first()

