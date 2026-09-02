import peewee
from .base import BaseModel


class Faction(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    code_name = peewee.CharField()