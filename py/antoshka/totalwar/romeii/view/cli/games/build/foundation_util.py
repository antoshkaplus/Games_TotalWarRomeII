from antoshka.totalwar.romeii.common.datetime import utc_now
from antoshka.totalwar.romeii.games.model import db as games_db, ProvinceBuild, ProvinceBuildKind
from antoshka.totalwar.romeii.games.db import list_control_plan_regions
from antoshka.totalwar.romeii.fixed.model import db as fixed_db, BuildingSuperchain
from antoshka.totalwar.romeii.fixed.db import (list_faction_buildings as fixed_db__list_faction_buildings)
from antoshka.totalwar.romeii.view.cli.games.util import get_selected_game, approx_province_by_name


def gen_foundation(province_name: str) -> games_db.ProvinceBuild:
    game = get_selected_game()
    faction_buildings = fixed_db__list_faction_buildings(game.faction_code)
    faction_buildings = list(fixed_db.Building.select().where(fixed_db.Building.code_name.in_(faction_buildings)))

    control_plan_regions = list_control_plan_regions(game.id)

    province = approx_province_by_name(province_name)
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
    return games_db.ProvinceBuild.create(game=game, ts=utc_now(), province_code=province.code_name,
                                          build=province_build.to_serializable(),
                                          status=ProvinceBuildKind.Foundation,
                                          status_ts=utc_now(),
                                          foundation=None)