import peewee
from .base import BaseModel
from .region import Region


class RegionEffects(BaseModel):
    region = peewee.ForeignKeyField(Region, backref='effects')
    effect_bundle = peewee.CharField()

    effect_name = peewee.CharField()
    scope = peewee.CharField()
    value = peewee.IntegerField()

    class Meta:
        indexes = (
            (('region', 'effect_name'), True),
        )