import itertools
from collections import defaultdict
from antoshka.totalwar.romeii.games.model import db as games_db
from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from antoshka.totalwar.romeii.regionsopt.stats import Stats
from antoshka.totalwar.romeii.regionsopt.fixed.building_api import list_buildings_stats
from .init_stats import make_province_init_stats


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


def make_regions_print_obj(regions_build: dict) -> list:
    region_print_obj_list = []
    for region_code, building_codes in regions_build.items():
        building_names = building_code_to_name(building_codes)
        buildings = {b_.code_name: b_ for b_ in fixed_db.Building.select().where(fixed_db.Building.code_name.in_(building_codes))}
        region_print_obj = {
            'code': region_code,
            'name': fixed_db.Region.get_by_id(region_code).settlement_name,
            'buildings': [{'code': c_,
                           'name': building_names[c_],
                           'cost': buildings[c_].create_cost} for c_ in building_codes]
        }
        region_print_obj_list.append(region_print_obj)
    return region_print_obj_list


def make_province_build_stats(province_build: games_db.ProvinceBuild) -> Stats:
    all_building_codes = list(itertools.chain(*[b_codes for b_codes in province_build.build['regions_build'].values()]))
    unique_building_codes = set(all_building_codes)
    building_stats = list_buildings_stats(unique_building_codes)
    stats = make_province_init_stats(province_build.province_code)
    stats += sum([building_stats[c_].province_stats for c_ in all_building_codes], Stats())
    return stats


def make_province_build_print_obj(province_build: games_db.ProvinceBuild,
                                  faction_init_stats: Stats) -> dict:
    stats = make_province_build_stats(province_build)
    province_print_obj = {
        'name': fixed_db.Province.get_by_id(province_build.province_code).province_name,
        'code': province_build.province_code,
        'id': province_build.id,
        'regions': make_regions_print_obj(province_build.build['regions_build']),
        'stats': stats.to_serializable(),
        'total_wealth': (stats + faction_init_stats).wealth
    }
    return province_print_obj