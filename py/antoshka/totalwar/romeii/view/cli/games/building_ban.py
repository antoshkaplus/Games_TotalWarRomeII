from antoshka.totalwar.romeii.common.datetime import utc_now
from antoshka.totalwar.romeii.view.cli.parser_util import add_parser
from antoshka.totalwar.romeii.games.model import db as games_db
from .util import get_selected_game


def add_building(args):
    game = get_selected_game()
    items = list(games_db.BuildingBan.select().where((games_db.BuildingBan.game == game) & (games_db.BuildingBan.building_code == args.building_code)))
    if len(items) != 0:
        print(f'Building `{args.building_code}` already present')
        return
    games_db.BuildingBan.create(game=game, building_code=args.building_code, ts=utc_now())
    print(f'Added `{args.building_code}` to current game: {game.campaign_code, game.faction_code}')


def attach_building_ban_parser(sps):
    p = sps.add_parser('bban', help='Ban building from Province Build optimization.')
    sps = p.add_subparsers()

    p = add_parser(sps, 'add', func=add_building)
    p.add_argument('building_code', type=str)