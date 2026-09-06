from .base import DB
from .building_effects import BuildingEffect
from .building_upgrade import BuildingUpgrade
from .faction import Faction
from .building_culture import BuildingCulture
from .building_culture_screen import BuildingCultureScreen
from .region_screen import RegionScreen
from .province_screen import ProvinceScreen
from .building import Building


def make_tables():
    DB.create_tables([BuildingEffect, BuildingUpgrade, Faction,
                      BuildingCulture, BuildingCultureScreen,
                      RegionScreen, ProvinceScreen, Building])
