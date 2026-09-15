from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from .faction_buildings import list_faction_buildings


def get_province_by_name(province_name: str) -> fixed_db.Province:
    return fixed_db.Province.select().where(fixed_db.Province.province_name == province_name).get()