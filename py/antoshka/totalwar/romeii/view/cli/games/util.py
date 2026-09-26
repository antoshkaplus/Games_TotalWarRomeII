from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from antoshka.totalwar.romeii.games.model import db as games_db
from antoshka.totalwar.romeii.games.db import list_control_plan_regions


def get_selected_game() -> games_db.Game:
    return games_db.Game.select().order_by(games_db.Game.last_selected.desc()).first()


def get_control_province_by_name(province_name: str) -> fixed_db.Province:
    game = get_selected_game()
    region_codes = list_control_plan_regions(game.id)
    regions = fixed_db.Region.select().join(fixed_db.Province).where(fixed_db.Region.code_name.in_(region_codes))

    for ro in regions:
        if ro.province.province_name == province_name:
            return ro.province
    raise RuntimeError()


def approx_province_by_name(province_name_prefix: str) -> fixed_db.Province:
    if len(province_name_prefix) <= 2:
        raise RuntimeError(f'Prefix `{province_name_prefix}` too short.')

    game = get_selected_game()

    start_pos = list(fixed_db.RegionStartPos.select()
                        .join(fixed_db.Region)
                        .join(fixed_db.Province)
                        .where(fixed_db.RegionStartPos.campaign_code_name == game.campaign_code))
    provinces = {s_.region.province.province_name: s_.region.province for s_ in start_pos}
    provinces = list(provinces.values())
    provinces = [p_ for p_ in provinces if p_.province_name.startswith(province_name_prefix)]

    if len(provinces) == 0:
        raise RuntimeError(f'No provinces found with prefix {province_name_prefix}')
    if len(provinces) > 1:
        raise RuntimeError(f'Multiple provinces with prefix {province_name_prefix}: {[p_.province_name for p_ in provinces]}')

    return provinces[0]
