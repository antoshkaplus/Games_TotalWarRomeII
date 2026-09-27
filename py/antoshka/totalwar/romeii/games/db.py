import typing as ty
from antoshka.totalwar.romeii.games.model import db as games_db


def list_control_plan_regions(game_id: int) -> ty.List[str]:
    """
    :return: region_code_names
    """
    return [ro.region_code for ro in games_db.RegionControlPlan.select().where(games_db.RegionControlPlan.game == game_id)]


def list_control_plan_region_codes(game_id: int) -> ty.List[str]:
    """
    :return: region_code_names
    """
    return [ro.region_code for ro in games_db.RegionControlPlan.select().where(games_db.RegionControlPlan.game == game_id)]
