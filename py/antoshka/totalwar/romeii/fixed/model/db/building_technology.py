import peewee
from .base import BaseModel
from .building import Building
from .technology import Technology


class BuildingTechnology(BaseModel):
    building = peewee.ForeignKeyField(Building)
    technology = peewee.ForeignKeyField(Technology)

    class Meta:
        indexes = (
            (('building', 'technology'), True),
        )