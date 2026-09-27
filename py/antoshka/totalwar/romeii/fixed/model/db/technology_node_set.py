import peewee
from .base import BaseModel


class TechnologyNodeSet(BaseModel):
    code_name = peewee.CharField(primary_key=True)
    campaign_code_name = peewee.CharField(null=True)
    faction = peewee.CharField(null=True)
    culture = peewee.CharField(null=True)
    subculture = peewee.CharField(null=True)
    category = peewee.CharField()