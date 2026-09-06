import peewee
from .base import BaseModel


class Province(BaseModel):
    code_name = peewee.CharField(primary_key=True)