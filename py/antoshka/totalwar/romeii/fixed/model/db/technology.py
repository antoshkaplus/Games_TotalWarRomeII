import peewee
from antoshka.totalwar.romeii.common.db import EnumCharField
from .base import BaseModel


class Technology(BaseModel):
    code_name = peewee.CharField(primary_key=True)
    research_points = peewee.IntegerField()
    cost_per_round = peewee.IntegerField()
