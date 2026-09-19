from antoshka.totalwar.romeii.common.datetime import utc_now
from antoshka.totalwar.romeii.games.model import db as games_db, ProvinceBuild, ProvinceBuildKind
from antoshka.totalwar.romeii.games.db import list_control_plan_regions
from antoshka.totalwar.romeii.fixed.model import db as fixed_db, BuildingSuperchain
from antoshka.totalwar.romeii.fixed.db import (get_province_by_name as fixed_db__get_province_by_name,
                                               list_faction_buildings as fixed_db__list_faction_buildings)
from antoshka.totalwar.romeii.regionsopt.fixed.building_api import list_buildings as opt_api__list_buildings
from antoshka.totalwar.romeii.regionsopt import solver_c1
from antoshka.totalwar.romeii.view.cli.parser_util import add_parser
from .util import get_selected_game
from collections import defaultdict
import pprint


def gen_foundation(args):
    game = get_selected_game()
    faction_buildings = fixed_db__list_faction_buildings(game.faction_code)
    faction_buildings = list(fixed_db.Building.select().where(fixed_db.Building.code_name.in_(faction_buildings)))

    control_plan_regions = list_control_plan_regions(game.id)

    province = fixed_db__get_province_by_name(args.province)
    regions = [ro for ro in province.regions if ro.code_name in control_plan_regions]

    start_pos = fixed_db.RegionStartPos.select().where(fixed_db.RegionStartPos.campaign_code_name == game.campaign_code,
                                                       fixed_db.RegionStartPos.region.in_(regions))
    start_pos = {sp.region.code_name: sp for sp in start_pos}

    province_build = {}
    for ro in regions:
        sp = start_pos[ro.code_name]
        region_build = []
        if sp.port:
            region_build.extend([bb.code_name for bb in faction_buildings if BuildingSuperchain(bb.superchain) == BuildingSuperchain.Port and bb.level == 0])

        if sp.province_capital:
            region_build.extend([bb.code_name for bb in faction_buildings if BuildingSuperchain(bb.superchain) == BuildingSuperchain.SettlementMajor and bb.level == 0])
        elif sp.resource:
            region_build.extend([bb.code_name for bb in faction_buildings if BuildingSuperchain(bb.superchain) == sp.resource and bb.level == 0])
        else:
            region_build.extend([bb.code_name for bb in faction_buildings if BuildingSuperchain(bb.superchain) == BuildingSuperchain.SettlementMinor and bb.level == 0])
        province_build[ro.code_name] = region_build

    province_build = ProvinceBuild(province.code_name, province_build)
    games_db.ProvinceBuild.create(game=game, ts=utc_now(), province_code=province.code_name,
                                  build=province_build.to_serializable(),
                                  status=ProvinceBuildKind.Foundation,
                                  status_ts=utc_now(),
                                  foundation=None)


def province_build_screen(pb: ProvinceBuild) -> ProvinceBuild:
    province_name = fixed_db.Province.get_by_id(pb.province_code).province_name
    named_regions_build = {}
    for  r_code, building_codes in pb.regions_build.items():
        r_name = fixed_db.Region.get_by_id(r_code).settlement_name
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

        building_names = [all_building_names[b_c] for b_c in building_codes]
        named_regions_build[r_name] = building_names
    return ProvinceBuild(province_name, named_regions_build)


def list_foundation(args):
    game = get_selected_game()
    foundations = games_db.ProvinceBuild.select().where(games_db.ProvinceBuild.game == game,
                                                        games_db.ProvinceBuild.status == ProvinceBuildKind.Foundation)
    if args.codes:
        for fo in foundations:
            pprint.pprint([f'id: {fo.id}', fo.build])
    else:
        for fo in foundations:
            pb = ProvinceBuild.from_serializable(fo.build)
            pb = province_build_screen(pb)
            pprint.pprint([f'id: {fo.id}', pb.to_serializable()])


def attach_foundation_parser(sps):
    p = sps.add_parser('foundation')
    sps = p.add_subparsers()

    p = add_parser(sps, 'gen', func=gen_foundation)
    p.add_argument('province', type=str)

    p = add_parser(sps, 'list', func=list_foundation)
    p.add_argument('--codes', action='store_true')


def opt_province(args):
    game = get_selected_game()
    fo = games_db.ProvinceBuild.get(args.foundation_id)

    # Missing extra stats
    buildings = opt_api__list_buildings(game.faction_code)
    buildings = {fb.name: fb for fb in buildings}


    foundation_build = ProvinceBuild.from_serializable(fo.build)
    region_name, region_build = map(list, zip(*foundation_build.regions_build.items()))
    capital = fixed_db.RegionStartPos.select().where(fixed_db.RegionStartPos.campaign_code_name == game.campaign_code,
                                                     fixed_db.RegionStartPos.region.in_(list(foundation_build.regions_build.keys())),
                                                     fixed_db.RegionStartPos.province_capital).get_or_none()

    port = list(fixed_db.RegionStartPos.select().where(fixed_db.RegionStartPos.campaign_code_name == game.campaign_code,
                                                       fixed_db.RegionStartPos.region.in_(list(foundation_build.regions_build.keys())),
                                                       fixed_db.RegionStartPos.port))
    port = [po.region.code_name for po in port]

    no_major = False
    if not capital:
        no_major = True
    else:
        idx = region_name.index(capital.region.code_name)
        region_name[idx], region_name[0] = region_name[0], region_name[idx]
        region_build[idx], region_build[0] = region_build[0], region_build[idx]

    port_idx = []
    for idx, ro in enumerate(region_name):
        if ro in port:
            port_idx.append(idx)

    params = solver_c1.Params(solver_c1.GameParams(buildings, solver_c1.Stats()),
                              solver_c1.ProvinceParams(region_build, port_idx, no_major),
                              solver_c1.SolutionParams(),
                              solver_c1.AlgoParams())
    solution = solver_c1.Solver().solve(params)
    if solution:
        print(solution)
        print('Solution Details:')
        for name, region in zip(region_name, solution.regions):
            # TODO: need region name here
            print(name)
            for building_name in region:
                # TODO: need building name here
                print(building_name, params.game_params.buildings[building_name].stats)

    regions_build = {region_code: list(build) for region_code, build in zip(region_name, solution.regions)}

    if not args.no_store:
        build = games_db.ProvinceBuild.create(game=game, ts=utc_now(),
                                              province_code=foundation_build.province_code,
                                              build=ProvinceBuild(foundation_build.province_code,
                                                                  regions_build).to_serializable(),
                                              status=ProvinceBuildKind.Secondary,
                                              status_ts=utc_now(),
                                              foundation=fo)
        print('New province build id:', build.id)


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


def attach_opt_parser(sps):
    p = add_parser(sps, 'opt', func=opt_province)
    p.add_argument('foundation_id', type=int)
    p.add_argument('--no-store', action='store_true')


def attach_build_parser(sps):
    p = sps.add_parser('build')
    sps = p.add_subparsers()

    p = add_parser(sps, 'list', func=list_builds)
    p.add_argument('--codes', action='store_true')

    attach_foundation_parser(sps)
    attach_opt_parser(sps)

    # foundation
    # list Province Name
    # gen Province Name

    # opt (no need to save it for now. Just be able to run would be enough.)
    # must provide foundation ID for that. Or can provide Province Name and will select latest foundation.
    # also must provide additional arguments.
