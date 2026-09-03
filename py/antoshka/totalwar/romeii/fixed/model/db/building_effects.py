import peewee
from .base import BaseModel


class BuildingEffect(BaseModel):
    code_name = peewee.CharField()
    effect_name = peewee.CharField()
    scope = peewee.CharField()
    value = peewee.IntegerField()
    value_damaged = peewee.IntegerField()
    value_ruined = peewee.IntegerField()

    class Meta:
        indexes = (
            (('code_name', 'effect_name'), True),
        )