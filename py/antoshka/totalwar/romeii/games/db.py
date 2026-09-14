import typing as ty
from antoshka.totalwar.romeii.games.model import db as games_db


def list_owned_regions(game_id: int) -> ty.List[str]:
    """
    :return: region_code_names
    """
    region_owner = [ro for ro in games_db.RegionOwner.select().where(games_db.RegionOwner.game == game_id)]
    region_owner = sorted(region_owner, key=lambda x: x.ts)
    region_owner = {ro.region_code: ro for ro in region_owner}
    region_codes = [ro.region_code for ro in region_owner.values() if ro.owner]
    return region_codes