from .base import DB
from .faction import Faction
from .province import Province
from .region import Region
from .province_religion import ProvinceReligion


def make_tables():
    DB.create_tables([Faction, Province, Region, ProvinceReligion])
