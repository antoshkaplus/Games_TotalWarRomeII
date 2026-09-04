from .base import DB
from .building_effects import BuildingEffect
from .building_upgrade import BuildingUpgrade
from .faction import Faction
from .building_culture import BuildingCulture


def make_tables():
    DB.create_tables([BuildingEffect, BuildingUpgrade, Faction, BuildingCulture])
