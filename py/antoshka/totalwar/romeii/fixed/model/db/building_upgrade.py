import peewee
from .base import BaseModel


class BuildingUpgrade(BaseModel):
    from_code_name = peewee.CharField()
    to_code_name = peewee.CharField()

    class Meta:
        indexes = (
            (('from_code_name', 'to_code_name'), True),
        )