from pprint import pprint
from playhouse.shortcuts import model_to_dict
from antoshka.totalwar.romeii.common.datetime import utc_now
from antoshka.totalwar.romeii.fixed.model.campaign_name import CAMPAIGN_CODE_TO_NAME
from antoshka.totalwar.romeii.games.model import db as games_db, ProvinceBuild, ProvinceBuildKind
from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from antoshka.totalwar.romeii.view.cli.parser_util import add_parser
from antoshka.totalwar.romeii.view.cli.games.util import get_selected_game, approx_province_by_name
from antoshka.totalwar.romeii.fixed.db import list_faction_buildings
from antoshka.totalwar.romeii.view.common.games.province_build import building_code_to_name, make_province_build_print_obj
from antoshka.totalwar.romeii.view.common.games.init_stats import make_faction_init_stats
from antoshka.totalwar.romeii.view.common.games.foundation import gen_foundation as gen_foundation_


def gen_foundation(args):
    province = approx_province_by_name(args.province)
    foundation = gen_foundation_(province.code_name)
    pprint(model_to_dict(foundation))


def province_build_screen(pb: ProvinceBuild) -> ProvinceBuild:
    province_name = fixed_db.Province.get_by_id(pb.province_code).province_name
    named_regions_build = {}
    for  r_code, building_codes in pb.regions_build.items():
        r_name = fixed_db.Region.get_by_id(r_code).settlement_name
        all_building_names = building_code_to_name(building_codes)

        building_names = [all_building_names[b_c] for b_c in building_codes]
        named_regions_build[r_name] = building_names
    return ProvinceBuild(province_name, named_regions_build)


def list_foundation(args):
    game = get_selected_game()
    foundations = list(games_db.ProvinceBuild.select().where(
                                        games_db.ProvinceBuild.game == game,
                                        games_db.ProvinceBuild.status == ProvinceBuildKind.Foundation))
    if args.province:
        province = approx_province_by_name(args.province)
        foundations = [f_ for f_ in foundations if f_.province_code == province.code_name]
        foundations.sort(key=lambda x: x.status_ts, reverse=True)
    else:
        foundations.sort(key=lambda x: x.status_ts)
        foundations = {f_.province_code: f_ for f_ in foundations}
        foundations = list(foundations.values())

    print_obj = {}

    resource_max_level = 2
    faction_init_stats = make_faction_init_stats(resource_max_level)
    print_obj['faction_stats'] = faction_init_stats.to_serializable()

    province_print_obj_list = []
    for f_ in foundations:
        province_print_obj = make_province_build_print_obj(f_, faction_init_stats)
        province_print_obj_list.append(province_print_obj)
    print_obj['foundations'] = province_print_obj_list
    pprint(print_obj)


def replace_building(args):
    game = get_selected_game()
    build = games_db.ProvinceBuild.get_by_id(args.foundation_id)
    if build.game.id != game.id:
        raise RuntimeError()
    if build.status != ProvinceBuildKind.Foundation:
        raise RuntimeError()

    all_building_codes = list_faction_buildings(game.faction_code, CAMPAIGN_CODE_TO_NAME[game.campaign_code])
    if args.from_building_code not in all_building_codes:
        raise RuntimeError()
    if args.to_building_code not in all_building_codes:
        raise RuntimeError()

    province_build = ProvinceBuild.from_serializable(build.build)
    idx = province_build.regions_build[args.region_code].index(args.from_building_code)
    province_build.regions_build[args.region_code][idx] = args.to_building_code

    build.build = province_build.to_serializable()
    build.save()


def add_building(args):
    game = get_selected_game()
    build = games_db.ProvinceBuild.get_by_id(args.foundation_id)
    if build.game.id != game.id:
        raise RuntimeError()
    if build.status != ProvinceBuildKind.Foundation:
        raise RuntimeError()

    all_building_codes = list_faction_buildings(game.faction_code, CAMPAIGN_CODE_TO_NAME[game.campaign_code])
    if args.building_code not in all_building_codes:
        raise RuntimeError()

    province_build = ProvinceBuild.from_serializable(build.build)
    province_build.regions_build[args.region_code].append(args.building_code)
    
    build.build = province_build.to_serializable()
    build.save()


def remove_building(args):
    game = get_selected_game()
    build = games_db.ProvinceBuild.get_by_id(args.foundation_id)
    if build.game.id != game.id:
        raise RuntimeError()
    if build.status != ProvinceBuildKind.Foundation:
        raise RuntimeError()

    all_building_codes = list_faction_buildings(game.faction_code, CAMPAIGN_CODE_TO_NAME[game.campaign_code])
    if args.building_code not in all_building_codes:
        raise RuntimeError()

    province_build = ProvinceBuild.from_serializable(build.build)
    province_build.regions_build[args.region_code].remove(args.building_code)
    
    build.build = province_build.to_serializable()
    build.save()

    
def select_foundation(args):
    game = get_selected_game()
    build = games_db.ProvinceBuild.get_by_id(args.foundation_id)
    if build.game.id != game.id:
        raise RuntimeError()
    if build.status != ProvinceBuildKind.Foundation:
        raise RuntimeError()

    build.status_ts = utc_now()
    build.save()
    print('Done')


def attach_foundation_parser(sps):
    p = sps.add_parser('foundation')
    sps = p.add_subparsers()

    p = add_parser(sps, 'gen', func=gen_foundation)
    p.add_argument('province', type=str)

    p = add_parser(sps, 'list', func=list_foundation, help='Displays primary foundation per province.')
    p.add_argument('--province', type=str)

    p = add_parser(sps, 'replace', func=replace_building)
    p.add_argument('foundation_id', type=int)
    p.add_argument('region_code', type=str)
    p.add_argument('from_building_code', type=str)
    p.add_argument('to_building_code', type=str)

    p = add_parser(sps, 'add', func=add_building)
    p.add_argument('foundation_id', type=int)
    p.add_argument('region_code', type=str)
    p.add_argument('building_code', type=str)

    p = add_parser(sps, 'remove', func=remove_building)
    p.add_argument('foundation_id', type=int)
    p.add_argument('region_code', type=str)
    p.add_argument('building_code', type=str)
    
    p = add_parser(sps, 'select', func=select_foundation)
    p.add_argument('foundation_id', type=int)
