import peewee
from antoshka.totalwar.romeii.games.model.db.game import Game
from antoshka.totalwar.romeii.common.db import UTC_DateTimeField
from .base import BaseModel


class RegionControlPlan(BaseModel):
    game = peewee.ForeignKeyField(Game, backref='regions_plan_control')
    region_code = peewee.CharField()
    ts = UTC_DateTimeField()

    class Meta:
        indexes = (
            (('game', 'region_code'), True),
        )