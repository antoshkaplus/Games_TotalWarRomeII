from .base import DB
from .game import Game
from .province_build import ProvinceBuild
from .region_control_plan import RegionControlPlan
from .building_ban import BuildingBan


def make_tables():
    DB.create_tables([Game, ProvinceBuild, RegionControlPlan, BuildingBan])