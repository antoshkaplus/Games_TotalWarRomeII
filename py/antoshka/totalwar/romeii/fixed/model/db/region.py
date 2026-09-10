import peewee
from .base import BaseModel
from .province import Province


class Region(BaseModel):
    code_name = peewee.CharField(primary_key=True)
    province = peewee.ForeignKeyField(Province, backref="regions")
    # region screen
    settlement_name = peewee.CharField()