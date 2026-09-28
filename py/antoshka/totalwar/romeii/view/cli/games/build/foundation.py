import itertools
from collections import defaultdict
from pprint import pprint
from playhouse.shortcuts import model_to_dict
from antoshka.totalwar.romeii.games.model import db as games_db, ProvinceBuild, ProvinceBuildKind
from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from antoshka.totalwar.romeii.regionsopt.stats import Stats
from antoshka.totalwar.romeii.view.cli.parser_util import add_parser
from antoshka.totalwar.romeii.view.cli.games.util import get_selected_game
from .foundation_util import gen_foundation as gen_foundation_
from .init_stats_util import make_faction_init_stats, make_province_init_stats
from antoshka.totalwar.romeii.regionsopt.fixed.building_api import list_buildings_stats


def gen_foundation(args):
    foundation = gen_foundation_(args.province)
    pprint(model_to_dict(foundation))


def building_code_to_name(building_codes: list[str]) -> dict[str,str]:
    bc_list = list(fixed_db.BuildingCulture.select()
                   .join(fixed_db.BuildingCultureScreen)
                   .where(fixed_db.BuildingCulture.building_code_name.in_(building_codes)))
    all_building_names = defaultdict(list)
    for bc in bc_list:
        all_building_names[bc.building_code_name].append(bc.screen.get().building_name)
    for _, names in all_building_names.items():
        if len(set(names)) > 1:
            raise RuntimeError()
    all_building_names = {code: names[0] for code, names in all_building_names.items()}
    return all_building_names


def province_build_screen(pb: ProvinceBuild) -> ProvinceBuild:
    province_name = fixed_db.Province.get_by_id(pb.province_code).province_name
    named_regions_build = {}
    for  r_code, building_codes in pb.regions_build.items():
        r_name = fixed_db.Region.get_by_id(r_code).settlement_name
        all_building_names = building_code_to_name(building_codes)

        building_names = [all_building_names[b_c] for b_c in building_codes]
        named_regions_build[r_name] = building_names
    return ProvinceBuild(province_name, named_regions_build)


def make_regions_print_obj(regions_build: dict) -> list:
    region_print_obj_list = []
    for region_code, building_codes in regions_build.items():
        building_names = building_code_to_name(building_codes)
        region_print_obj = {
            'code': region_code,
            'name': fixed_db.Region.get_by_id(region_code).settlement_name,
            'buildings': [{'code': c_,
                           'name': building_names[c_]} for c_ in building_codes]
        }
        region_print_obj_list.append(region_print_obj)
    return region_print_obj_list


def list_foundation(_):
    game = get_selected_game()
    foundations = list(games_db.ProvinceBuild.select().where(
                                        games_db.ProvinceBuild.game == game,
                                        games_db.ProvinceBuild.status == ProvinceBuildKind.Foundation))
    foundations.sort(key=lambda x: x.status_ts)
    foundations = {f_.province_code: f_ for f_ in foundations}
    foundations = list(foundations.values())

    print_obj = {}

    resource_max_level = 2
    faction_init_stats = make_faction_init_stats(resource_max_level)
    print_obj['faction_stats'] = faction_init_stats.to_serializable()

    province_print_obj_list = []
    for f_ in foundations:
        all_building_codes = list(itertools.chain(*[b_codes for b_codes in f_.build['regions_build'].values()]))
        unique_building_codes = set(all_building_codes)
        building_stats = list_buildings_stats(unique_building_codes)
        stats = make_province_init_stats(f_.province_code)
        stats += sum([building_stats[c_].province_stats for c_ in all_building_codes], Stats())
        province_print_obj = {
            'name': fixed_db.Province.get_by_id(f_.province_code).province_name,
            'code': f_.province_code,
            'id': f_.id,
            'regions': make_regions_print_obj(f_.build['regions_build']),
            'stats': stats.to_serializable(),
            'total_wealth': (stats + faction_init_stats).wealth
        }

        province_print_obj_list.append(province_print_obj)
    print_obj['foundations'] = province_print_obj_list
    pprint(print_obj)


def attach_foundation_parser(sps):
    p = sps.add_parser('foundation')
    sps = p.add_subparsers()

    p = add_parser(sps, 'gen', func=gen_foundation)
    p.add_argument('province', type=str)

    add_parser(sps, 'list', func=list_foundation, help='Displays primary foundation per province.')