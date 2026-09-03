from .base import DB
from .building_effects import BuildingEffect
from .building_upgrade import BuildingUpgrade


def make_tables():
    DB.create_tables([BuildingEffect, BuildingUpgrade])
