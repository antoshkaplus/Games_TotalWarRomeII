import typing as ty
from antoshka.totalwar.romeii.common.datetime import utc_now
from antoshka.totalwar.romeii.fixed.model.campaign_name import CAMPAIGN_CODE_TO_NAME
from antoshka.totalwar.romeii.games.model import db as games_db, ProvinceBuild, ProvinceBuildKind
from antoshka.totalwar.romeii.games.db import list_control_plan_regions
from antoshka.totalwar.romeii.fixed.model import db as fixed_db, BuildingSuperchain
from antoshka.totalwar.romeii.fixed.db import (list_faction_buildings as fixed_db__list_faction_buildings)
from antoshka.totalwar.romeii.regionsopt.fixed.building_api import list_buildings as opt_api__list_buildings
from antoshka.totalwar.romeii.regionsopt.fixed import building_api
from antoshka.totalwar.romeii.regionsopt import solver_c1
from antoshka.totalwar.romeii.view.cli.parser_util import add_parser
from .util import get_selected_game
from collections import defaultdict
import pprint
from antoshka.totalwar.romeii.regionsopt.stats import Stats
from antoshka.totalwar.romeii.regionsopt.fixed import effect_map
from .util import get_control_province_by_name


def gen_foundation(args):
    game = get_selected_game()
    faction_buildings = fixed_db__list_faction_buildings(game.faction_code)
    faction_buildings = list(fixed_db.Building.select().where(fixed_db.Building.code_name.in_(faction_buildings)))

    control_plan_regions = list_control_plan_regions(game.id)

    province = get_control_province_by_name(args.province)
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


def make_init_stats(province_code: str, resource_max_level: ty.Optional[int] = None) -> Stats:
    """
    :param province_code:
    :param resource_max_level:
    :return:
    """
    init_stats = Stats()
    game = get_selected_game()
    plan_control_region_codes = [p_.region_code for p_ in game.regions_plan_control]

    province_regions = fixed_db.Region.select().where(fixed_db.Region.code_name.in_(plan_control_region_codes) & (fixed_db.Region.province == province_code))
    effects = fixed_db.RegionEffects.select().where(fixed_db.RegionEffects.region.in_(province_regions))
    init_stats += effect_map.effects_to_stats(effects).province_stats

    # Add Regions Faction-wide Stats
    effects = fixed_db.RegionEffects.select().where(fixed_db.RegionEffects.region.in_(plan_control_region_codes))
    init_stats += effect_map.effects_to_stats(effects).faction_stats

    # Add Resource Faction-wide Stats.
    start_pos = fixed_db.RegionStartPos.select().where(fixed_db.RegionStartPos.campaign_code_name == game.campaign_code,
                                                       fixed_db.RegionStartPos.region.in_(plan_control_region_codes))
    resources = [s_.resource for s_ in start_pos if s_.resource]

    buildings_code_names = fixed_db__list_faction_buildings(game.faction_code, CAMPAIGN_CODE_TO_NAME[game.campaign_code])
    buildings = fixed_db.Building.select().where(fixed_db.Building.code_name.in_(buildings_code_names))
    if resource_max_level:
        # Some resources may have unit buff branching. But usual stats usually increase the same still.
        resource_buildings = {BuildingSuperchain(b_.superchain): b_.code_name for b_ in buildings
                              if BuildingSuperchain(b_.superchain).resource_kind and b_.level == resource_max_level-1}
    else:
        resource_buildings = {}
        for b_ in buildings:
            s_chain = BuildingSuperchain(b_.superchain)
            if s_chain.resource_kind and (s_chain not in resource_buildings or b_.level > resource_buildings[s_chain].level):
                resource_buildings[s_chain] = b_
        resource_buildings = {s_chain: b_.code_name for s_chain, b_ in resource_buildings.items()}

    province_resource_buildings = [resource_buildings[r_] for r_ in resources]
    stats = building_api.list_buildings_stats(set(province_resource_buildings))
    stats = sum([stats[building_code] for building_code in province_resource_buildings],
                start=building_api.ProvinceFactionStats())

    init_stats += stats.faction_stats

    # Add Faction and Political Party Effects Stats
    effects = fixed_db.FactionEffect.select().where((fixed_db.FactionEffect.faction == game.faction_code)
                                                      & ((fixed_db.FactionEffect.political_party == game.political_party)
                                                         | (fixed_db.FactionEffect.political_party.is_null())))
    init_stats += effect_map.effects_to_stats(effects).faction_stats
    return init_stats


def opt_province(args):
    game = get_selected_game()
    fo = games_db.ProvinceBuild.get(args.foundation_id)

    buildings = opt_api__list_buildings(game.faction_code)
    buildings = {fb.name: fb for fb in buildings}

    b_technology = list(fixed_db.BuildingTechnology
                            .select()
                            .join(fixed_db.Technology)
                            .where(fixed_db.BuildingTechnology.building.in_(list(buildings))))
    b_technology = {b_.building.code_name: b_.technology.research_points for b_ in b_technology}
    print('Before')
    print(b_technology)

    for b_name, research_points in b_technology.items():
        if research_points >= 800:
            buildings.pop(b_name, None)
    b_technology = {b_name: research_points
                    for b_name, research_points in b_technology.items()
                    if not (research_points >= 800)}

    print('After')
    print(b_technology)

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
