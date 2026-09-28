from pprint import pprint
from collections import defaultdict
from antoshka.totalwar.romeii.games.db import list_control_plan_regions
from antoshka.totalwar.romeii.games.model import db as games_db, ProvinceBuild, ProvinceBuildKind
from antoshka.totalwar.romeii.view.cli.games.util import get_selected_game
from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from antoshka.totalwar.romeii.regionsopt.fixed.building_api import list_buildings as opt_api__list_buildings
from antoshka.totalwar.romeii.view.common.games.foundation import get_selected_foundation
from antoshka.totalwar.romeii.view.common.games.init_stats import make_province_init_stats, make_faction_init_stats
from antoshka.totalwar.romeii.view.common.games.province_build import make_province_build_print_obj, \
    make_province_build_stats
from ...parser_util import add_parser


def list_init_stats(_):
    game = get_selected_game()
    resource_max_level = 2
    print_obj = {}
    faction_init_stats = make_faction_init_stats(resource_max_level)
    print_obj['faction'] = faction_init_stats.to_serializable()

    control_plan = games_db.RegionControlPlan.select().where(games_db.RegionControlPlan.game == game)
    region_codes = [c_.region_code for c_ in control_plan]
    provinces = list(fixed_db.Province.select().join(fixed_db.Region).where(fixed_db.Region.code_name.in_(region_codes)).distinct())
    print_provinces_obj = print_obj['provinces'] = {}
    for p_ in provinces:
        init_stats = make_province_init_stats(p_.code_name)
        print_provinces_obj[f'{p_.province_name} ({p_.code_name})'] = init_stats.to_serializable()
    pprint(print_obj)


def list_building_tech(_):
    game = get_selected_game()

    buildings = opt_api__list_buildings(game.faction_code)
    buildings = {fb.name: fb for fb in buildings}

    b_technology = list(fixed_db.BuildingTechnology
                        .select()
                        .join(fixed_db.Technology)
                        .where(fixed_db.BuildingTechnology.building.in_(list(buildings))))

    tech_buildings = defaultdict(dict)
    for b_ in b_technology:
        obj = tech_buildings[b_.technology.code_name]
        obj['research_points'] = b_.technology.research_points
        if 'buildings' not in obj:
            obj['buildings'] = []
        obj['buildings'].append(b_.building.code_name)

    pprint(tech_buildings)


def list_builds(args):
    game = get_selected_game()
    builds = list(games_db.ProvinceBuild.select().where(games_db.ProvinceBuild.game == game,
                                                        games_db.ProvinceBuild.status != ProvinceBuildKind.Archived))

    builds.sort(key=lambda x: x.status_ts)
    builds = {f_.province_code: f_ for f_ in builds}


    region_codes = list_control_plan_regions(game.id)
    provinces = fixed_db.Province.select().join(fixed_db.Region).where(fixed_db.Region.code_name.in_(region_codes)).distinct()
    province_codes = [p_.code_name for p_ in provinces]

    for c_ in province_codes:
        if c_ not in builds:
            builds[c_] = get_selected_foundation(c_)
    builds = list(builds.values())

    print_obj = {}

    resource_max_level = 2
    faction_init_stats = make_faction_init_stats(resource_max_level)
    print_obj['faction_stats'] = faction_init_stats.to_serializable()

    province_print_obj_list = []
    total_food = faction_init_stats.food
    for f_ in builds:
        total_food += make_province_build_stats(f_).food
        province_print_obj = make_province_build_print_obj(f_, faction_init_stats)
        province_print_obj_list.append(province_print_obj)
    print_obj['builds'] = province_print_obj_list

    print_obj['total_food'] = total_food
    pprint(print_obj)


def attach_build_commands(sps):
    add_parser(sps, 'list-init-stats', func=list_init_stats)
    add_parser(sps, 'list-building-tech', func=list_building_tech)


    p = add_parser(sps, 'list', func=list_builds, help='List latest build per province. '
                                                              'If no build - use foundation.')