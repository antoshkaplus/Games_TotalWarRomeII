import typing as ty
from antoshka.totalwar.romeii.fixed.model.campaign_name import CAMPAIGN_CODE_TO_NAME
from antoshka.totalwar.romeii.fixed.model import db as fixed_db, BuildingSuperchain
from antoshka.totalwar.romeii.fixed.db import (list_faction_buildings as fixed_db__list_faction_buildings)
from antoshka.totalwar.romeii.regionsopt.fixed import building_api
from antoshka.totalwar.romeii.view.cli.games.util import get_selected_game
from antoshka.totalwar.romeii.regionsopt.stats import Stats
from antoshka.totalwar.romeii.regionsopt.fixed import effect_map
from antoshka.totalwar.romeii.games.db import list_control_plan_region_codes


def make_province_init_stats(province_code: str) -> Stats:
    game = get_selected_game()
    region_codes = list_control_plan_region_codes(game.id)
    province_regions = fixed_db.Region.select().where(fixed_db.Region.code_name.in_(region_codes) & (fixed_db.Region.province == province_code))
    effects = fixed_db.RegionEffects.select().where(fixed_db.RegionEffects.region.in_(province_regions))
    return effect_map.effects_to_stats(effects).province_stats


def make_faction_init_stats(resource_max_level: ty.Optional[int] = None) -> Stats:
    game = get_selected_game()
    region_codes = list_control_plan_region_codes(game.id)

    init_stats = Stats()
    # Add Regions Faction-wide Stats
    effects = fixed_db.RegionEffects.select().where(fixed_db.RegionEffects.region.in_(region_codes))
    init_stats += effect_map.effects_to_stats(effects).faction_stats

    # Add Resource Faction-wide Stats.
    start_pos = fixed_db.RegionStartPos.select().where(fixed_db.RegionStartPos.campaign_code_name == game.campaign_code,
                                                       fixed_db.RegionStartPos.region.in_(region_codes))
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


def make_init_stats(province_code: str, resource_max_level: ty.Optional[int] = None) -> Stats:
    """
    :param province_code:
    :param resource_max_level:
    :return:
    """
    init_stats = make_province_init_stats(province_code)
    init_stats += make_faction_init_stats(resource_max_level)
    return init_stats