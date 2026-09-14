from antoshka.totalwar.romeii.games.model import db
from antoshka.config import get_games_db_path


# There is no need to insert anything in the database.
db.DB.init(get_games_db_path())
db.make_tables()


