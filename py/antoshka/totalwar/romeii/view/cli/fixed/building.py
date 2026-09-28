from pprint import pprint
from playhouse.shortcuts import model_to_dict
from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from antoshka.totalwar.romeii.view.cli.parser_util import add_parser
from antoshka.totalwar.romeii.regionsopt.fixed.building_api import list_buildings_stats


def show_building(args):
    b = fixed_db.Building.get_by_id(args.code_name)
    b = model_to_dict(b)

    stats = list_buildings_stats([args.code_name])[args.code_name]
    b['stats'] = stats.to_serializable()

    pprint(b)


def attach_building_parser(sps):
    p = add_parser(sps, 'building', func=show_building)
    p.add_argument('code_name', type=str)