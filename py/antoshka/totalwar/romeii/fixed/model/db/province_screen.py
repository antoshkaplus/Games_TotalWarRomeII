import peewee
from .base import BaseModel


class ProvinceScreen(BaseModel):
    province_code_name = peewee.CharField(primary_key=True)
    province_name = peewee.CharField()
