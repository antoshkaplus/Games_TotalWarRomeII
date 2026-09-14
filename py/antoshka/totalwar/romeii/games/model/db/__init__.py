from .base import DB
from .game import Game
from .province_build import ProvinceBuild
from .region_control_plan import RegionControlPlan


def make_tables():
    DB.create_tables([Game, ProvinceBuild, RegionControlPlan])