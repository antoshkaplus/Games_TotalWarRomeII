from .base import DB
from .faction import Faction
from .province import Province
from .region import Region
from .province_religion import ProvinceReligion
from .region_building_slot import RegionBuildingSlot


def make_tables():
    DB.create_tables([Faction, Province, Region, ProvinceReligion, RegionBuildingSlot])
