import peewee
from .base import BaseModel


class RegionScreen(BaseModel):
    region_code_name = peewee.CharField(primary_key=True)
    region_name = peewee.CharField()
