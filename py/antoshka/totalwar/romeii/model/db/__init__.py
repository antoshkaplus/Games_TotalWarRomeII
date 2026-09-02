from .base import DB
from .faction import Faction
from .province import Province
from .region import Region


def make_tables():
    DB.create_tables([Faction, Province, Region])
