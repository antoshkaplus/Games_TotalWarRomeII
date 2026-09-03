import peewee
from .base import BaseModel
from .province import Province


class ProvinceReligion(BaseModel):
    province = peewee.ForeignKeyField(Province, backref='religions')
    religion_code_name = peewee.CharField()
    ratio = peewee.FloatField()

    class Meta:
        indexes = (
            (('province', 'religion_code_name'), True),
        )