import peewee
from .base import BaseModel
from .building_culture import BuildingCulture


class BuildingCultureScreen(BaseModel):
    building_culture = peewee.ForeignKeyField(BuildingCulture, primary_key=True, backref='screen')
    building_name = peewee.CharField()
    short_description = peewee.CharField()
