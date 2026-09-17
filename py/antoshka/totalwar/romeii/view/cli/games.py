import typing as ty
from collections import defaultdict
from antoshka.totalwar.romeii.common.datetime import utc_now
from antoshka.totalwar.romeii.games.model import db as games_db, ProvinceBuild, ProvinceBuildKind
from antoshka.totalwar.romeii.games.db import list_control_plan_regions
from antoshka.totalwar.romeii.fixed.model import db as fixed_db, BuildingSuperchain
from antoshka.totalwar.romeii.fixed.model.campaign_name import CampaignName, CAMPAIGN_NAME_TO_CODE
from antoshka.totalwar.romeii.fixed.db import (get_province_by_name as fixed_db__get_province_by_name,
                                               list_faction_buildings as fixed_db__list_faction_buildings)
from antoshka.totalwar.romeii.regionsopt.fixed.building_api import list_buildings as opt_api__list_buildings
from antoshka.totalwar.romeii.regionsopt import apply_solver as opt_solver
from .parser_util import add_parser


def get_selected_game():
    return games_db.Game.select().order_by(games_db.Game.last_selected.desc()).first()


def create_game_manually(args):
    campaign_name = CampaignName(args.campaign)
    faction = fixed_db.Faction.select().where(fixed_db.Faction.screen_name == args.faction).get()
    now = utc_now()

    game = games_db.Game.create(campaign_code=CAMPAIGN_NAME_TO_CODE[campaign_name],
                                faction_code=faction.code_name,
                                create_ts=now,
                                last_selected=now)

    print('Created new game:',
          game.id, game.campaign_code, game.faction_code,
          game.create_ts, game.last_selected)


def attach_create_game_parser(sps):
    p = sps.add_parser('create')
    sps = p.add_subparsers()

    p = add_parser(sps, 'manually', func=create_game_manually)
    p.add_argument('campaign', type=str)
    p.add_argument('faction', type=str)

    # add_parser(sps, 'from-save')


def add_region(args):
    game = get_selected_game()

    conditions = [fixed_db.RegionStartPos.campaign_code_name == game.campaign_code,
                  fixed_db.Region.settlement_name.startswith(args.region)]
    regions = list(fixed_db.Region.select()
                                .join(fixed_db.RegionStartPos)
                                .where(*conditions))
    if len(regions) == 0:
        print('Region not found')
    elif len(regions) > 1:
        print(f'Multiple regions found: {(rr.settlement_name for rr in regions)}')
    else:
        regions = regions[0]
        region_owner = games_db.RegionControlPlan.create(game=game,
                                                         ts=utc_now(),
                                                         region_code=regions.code_name)
        print(f'Game (id={game.id}) own region (code={region_owner.region_code})')


def attach_region_parser(sps):
    p = sps.add_parser('region')
    sps = p.add_subparsers()

    p = add_parser(sps, 'add', func=add_region)
    p.add_argument('region', type=str)


def list_provinces(_):
    game = get_selected_game()
    region_codes = list_control_plan_regions(game.id)

    regions = fixed_db.Region.select().where(fixed_db.Region.code_name.in_(region_codes))
    regions_start_pos = fixed_db.RegionStartPos.select().where(
        fixed_db.RegionStartPos.campaign_code_name == game.campaign_code,
        fixed_db.RegionStartPos.region.in_(regions))

    provinces = defaultdict(list)
    for ro in regions:
        provinces[ro.province.province_name].append(ro.settlement_name)
    for po_name, ro_names in provinces.items():
        print(po_name, ':', ro_names)


def optimize_province(args):
    # TODO: figure out foundation.
    game = get_selected_game()

    owned_regions = list_control_plan_regions(game.id)
    province = fixed_db__get_province_by_name(args.province)

    regions = [ro for ro in province.regions if ro.code_name in owned_regions]
    regions: ty.List[fixed_db.Region]

    # need to figure out which one is Capital, resources and Capital region.


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


def list_foundation(args):
    game = get_selected_game()
    foundations = games_db.ProvinceBuild.select().where(games_db.ProvinceBuild.game == game,
                                                       games_db.ProvinceBuild.status == ProvinceBuildKind.Foundation)
    for fo in foundations:
        print(fo.id, fo.province_code, fo.build)


def attach_foundation_parser(sps):
    p = sps.add_parser('foundation')
    sps = p.add_subparsers()

    p = add_parser(sps, 'gen', func=gen_foundation)
    p.add_argument('province', type=str)

    p = add_parser(sps, 'list', func=list_foundation)
    # p.add_argument('--province', type=str)


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

    params = opt_solver.ApplySolverParams(opt_solver.GameParams(buildings, opt_solver.Stats()),
                                          opt_solver.ProvinceParams(region_build, port_idx, no_major),
                                          opt_solver.SolutionParams(),
                                          opt_solver.AlgoParams())
    solution = opt_solver.apply_solver(params)
    if solution:
        print(solution)
        print('Solution Details:')
        for name, region in zip(region_name, solution.regions):
            print(name)
            for building_name in region:
                print(building_name, params.game_params.buildings[building_name].stats)

    regions_build = {region_code: list(build) for region_code, build in zip(region_name, solution.regions)}
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
    p.add_argument('foundation_id', type=int)


def attach_build_parser(sps):
    p = sps.add_parser('build')
    sps = p.add_subparsers()

    attach_foundation_parser(sps)
    attach_opt_parser(sps)

    # foundation
    # list Province Name
    # gen Province Name

    # opt (no need to save it for now. Just be able to run would be enough.)
    # must provide foundation ID for that. Or can provide Province Name and will select latest foundation.
    # also must provide additional arguments.


def attach_games_parser(sps):
    p = sps.add_parser('games')
    sps = p.add_subparsers()

    attach_create_game_parser(sps)
    attach_region_parser(sps)
    attach_build_parser(sps)

    add_parser(sps, 'list-provinces', func=list_provinces)
    p = add_parser(sps, 'opt-province', func=optimize_province)
    p.add_argument('province')

    # build province

    # province optimize - see regions, will know names, capital and cpecial effect.