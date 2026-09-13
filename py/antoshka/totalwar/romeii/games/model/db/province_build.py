import peewee
from antoshka.totalwar.romeii.common.db import UTC_DateTimeField, EnumCharField
from .base import BaseModel
from .game import Game
from antoshka.totalwar.romeii.games.model.province_build_status import ProvinceBuildStatus


class ProvinceBuild(BaseModel):
    game = peewee.ForeignKeyField(Game, backref='province_builds')
    ts = UTC_DateTimeField()
    province_code = peewee.CharField()
    build = peewee.JSONField()

    status = EnumCharField(ProvinceBuildStatus)
    status_ts = UTC_DateTimeField()

    class Meta:
        indexes = (
            (('game', 'province_code', 'build'), True),
        )