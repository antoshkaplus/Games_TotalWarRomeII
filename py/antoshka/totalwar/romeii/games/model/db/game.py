import peewee
# noinspection PyUnresolvedReferences
from playhouse.sqlite_ext import AutoIncrementField
from antoshka.totalwar.romeii.common.db import UTC_DateTimeField
from .base import BaseModel


class Game(BaseModel):
    id = AutoIncrementField(primary_key=True)
    campaign_code = peewee.CharField()
    faction_code = peewee.CharField()
    # During game creation look up in fixed_db.
    # Populate if single, ask user to specify if multiple.
    political_party = peewee.CharField()
    create_ts = UTC_DateTimeField()
    save_file_game_id = peewee.CharField(unique=True, null=True)
    # Should be selected once created.
    last_selected = UTC_DateTimeField()

    class Meta:
        indexes = (
            (('campaign_code', 'faction_code', 'create_ts'), True),
        )