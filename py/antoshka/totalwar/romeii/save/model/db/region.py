import peewee
from .base import BaseModel
from .faction import Faction
from .province import Province


class Region(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    code_name = peewee.CharField()
    province = peewee.ForeignKeyField(Province, backref='regions')
    province_capital = peewee.BooleanField(default=False)
    owner = peewee.ForeignKeyField(Faction, backref='regions')