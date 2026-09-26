import argparse
import peewee
from playhouse.migrate import SqliteMigrator, migrate
from antoshka.config import get_games_db_path
from antoshka.totalwar.romeii.view.cli.parser_util import add_parser
from antoshka.totalwar.romeii.games.model import db


db.DB.init(get_games_db_path())
db.make_tables()


# Not needed any longer
def add_game_political_party(_):
    migrator = SqliteMigrator(db.DB)
    political_party = peewee.CharField()
    migrate(migrator.add_column('game', 'political_party', political_party))
    print('Ok')


parser = argparse.ArgumentParser(description='Games file db')
sps = parser.add_subparsers()


add_parser(sps, 'add-game-political-party', func=add_game_political_party)


args = parser.parse_args()
args.func(args)

