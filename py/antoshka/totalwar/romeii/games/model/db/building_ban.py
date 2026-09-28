import peewee
from antoshka.totalwar.romeii.common.db import UTC_DateTimeField
from .base import BaseModel
from .game import Game


class BuildingBan(BaseModel):
    game = peewee.ForeignKeyField(Game, backref='building_bans')
    building_code = peewee.CharField()
    ts = UTC_DateTimeField()

    class Meta:
        indexes = (
            (('game', 'building_code'), True),
        )