import peewee
# noinspection PyUnresolvedReferences
from playhouse.sqlite_ext import AutoIncrementField
from antoshka.totalwar.romeii.common.db import UTC_DateTimeField, EnumCharField
from .base import BaseModel
from .game import Game
from antoshka.totalwar.romeii.games.model.province_build_kind import ProvinceBuildKind


class ProvinceBuild(BaseModel):
    id = AutoIncrementField(primary_key=True)
    game = peewee.ForeignKeyField(Game, backref='province_builds')
    ts = UTC_DateTimeField()
    province_code = peewee.CharField()
    build = peewee.JSONField()

    status = EnumCharField(ProvinceBuildKind)
    # Whenever status changes, `status_ts` must change too.
    status_ts = UTC_DateTimeField()

    foundation = peewee.ForeignKeyField('self', null=True)

    class Meta:
        indexes = (
            (('game', 'province_code', 'build'), True),
        )