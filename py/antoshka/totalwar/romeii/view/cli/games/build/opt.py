from playhouse.shortcuts import model_to_dict
from antoshka.totalwar.romeii.common.datetime import utc_now
from antoshka.totalwar.romeii.games.model import db as games_db, ProvinceBuild, ProvinceBuildKind
from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from antoshka.totalwar.romeii.regionsopt import solver_c1
from antoshka.totalwar.romeii.view.cli.parser_util import add_parser
from antoshka.totalwar.romeii.view.cli.games.util import get_selected_game
from .init_stats_util import make_init_stats
from .foundation_util import gen_foundation
from antoshka.totalwar.romeii.view.cli.games.util import approx_province_by_name
from .building_util import list_buildings_by_research_points


def opt_province(args):
    game = get_selected_game()
    buildings = list_buildings_by_research_points()

    foundation_id = None
    if args.foundation_id:
        foundation_id = args.foundation_id
    else:
        province = approx_province_by_name(args.province_name)
        foundations = list(games_db.ProvinceBuild.select().where((games_db.ProvinceBuild.game == game)
                                              & games_db.ProvinceBuild.foundation.is_null()
                                              & (games_db.ProvinceBuild.province_code == province.code_name)).order_by(games_db.ProvinceBuild.status_ts.desc()))
        if not foundations:
            # Try to pick up latest foundation for province first.
            foundations = [gen_foundation(args.province_name)]
        foundation_id = foundations[0]

    fo = games_db.ProvinceBuild.get_by_id(foundation_id)
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

    # Can add more parameters: init_stats buildings depth, solution params buildings depth.
    params = solver_c1.Params(solver_c1.GameParams(buildings, make_init_stats(foundation_build.province_code)),
                              solver_c1.ProvinceParams(region_build, port_idx, no_major),
                              solver_c1.SolutionParams(args.min_food, args.min_order),
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


def attach_opt_parser(sps):
    p = add_parser(sps, 'opt', func=opt_province)
    # One way doing it by foundation id.
    # Another way should be by province name with latest foundation.
    # If no such foundation found - generate one.
    group = p.add_mutually_exclusive_group()
    group.add_argument('--foundation-id', type=int)
    group.add_argument('--province-name', type=str)
    p.add_argument('--no-store', action='store_true')
    p.add_argument('--min-food', type=int, default=0)
    p.add_argument('--min-order', type=int, default=0)


