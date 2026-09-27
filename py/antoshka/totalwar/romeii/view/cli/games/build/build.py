import pprint
from collections import defaultdict
from antoshka.totalwar.romeii.games.model import db as games_db, ProvinceBuild, ProvinceBuildKind
from antoshka.totalwar.romeii.view.cli.games.util import get_selected_game
from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from antoshka.totalwar.romeii.regionsopt.fixed.building_api import list_buildings as opt_api__list_buildings
from .init_stats_util import make_province_init_stats, make_faction_init_stats
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
    pprint.pprint(print_obj)


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

    pprint.pprint(tech_buildings)


def list_builds(args):
    game = get_selected_game()
    foundations = games_db.ProvinceBuild.select().where(games_db.ProvinceBuild.game == game,
                                                        games_db.ProvinceBuild.status != ProvinceBuildKind.Foundation)
    if args.codes:
        for fo in foundations:
            pprint.pprint([f'id: {fo.id}', fo.build])
    else:
        for fo in foundations:
            pb = ProvinceBuild.from_serializable(fo.build)
            pb = province_build_screen(pb)
            pprint.pprint([f'id: {fo.id}', pb.to_serializable()])


def attach_build_commands(sps):
    add_parser(sps, 'list-init-stats', func=list_init_stats)
    add_parser(sps, 'list-building-tech', func=list_building_tech)


    p = add_parser(sps, 'list', func=list_builds)
    p.add_argument('--codes', action='store_true')