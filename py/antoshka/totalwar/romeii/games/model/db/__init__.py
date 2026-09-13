from .base import DB
from .game import Game
from .province_build import ProvinceBuild
from .region_owner import RegionOwner


def make_tables():
    DB.create_tables([Game, ProvinceBuild, RegionOwner])