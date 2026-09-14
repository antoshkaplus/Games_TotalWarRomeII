import argparse
from antoshka.totalwar.romeii.view.cli import attach_games_parser
from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from antoshka.totalwar.romeii.games.model import db as games_db
from antoshka.config import get_games_db_path, get_fixed_db_path


fixed_db.DB.init(get_fixed_db_path())
games_db.DB.init(get_games_db_path())


parser = argparse.ArgumentParser(description='Total War Rome II CLI')
sps = parser.add_subparsers()

attach_games_parser(sps)

args = parser.parse_args()
args.func(args)


