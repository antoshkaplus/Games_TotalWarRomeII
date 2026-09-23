from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from antoshka.totalwar.romeii.games.model import db as games_db
from antoshka.totalwar.romeii.games.db import list_control_plan_regions


def get_selected_game() -> games_db.Game:
    return games_db.Game.select().order_by(games_db.Game.last_selected.desc()).first()


def get_province_by_name(province_name: str) -> fixed_db.Province:
    game = get_selected_game()
    region_codes = list_control_plan_regions(game.id)
    regions = fixed_db.Region.select().join(fixed_db.Province).where(fixed_db.Region.code_name.in_(region_codes))

    for ro in regions:
        if ro.province.province_name == province_name:
            return ro.province
    raise RuntimeError()