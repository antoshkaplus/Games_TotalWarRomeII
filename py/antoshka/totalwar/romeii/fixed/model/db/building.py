import peewee
from .base import BaseModel


class Building(BaseModel):
    code_name = peewee.CharField(primary_key=True)
    chain = peewee.CharField()
    superchain = peewee.CharField()

    level = peewee.IntegerField()
    create_turns = peewee.IntegerField()
    create_cost = peewee.IntegerField()
    resource_requirement = peewee.CharField(null=True)