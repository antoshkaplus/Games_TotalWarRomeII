import peewee
from antoshka.totalwar.romeii.games.model.db.game import Game
from antoshka.totalwar.romeii.common.db import UTC_DateTimeField
from .base import BaseModel


class RegionOwner(BaseModel):
    game = peewee.ForeignKeyField(Game)
    ts = UTC_DateTimeField()
    region_code = peewee.CharField()
    owner = peewee.BooleanField()
