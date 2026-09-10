import peewee
from antoshka.totalwar.romeii.common.db import EnumCharField
from antoshka.totalwar.romeii.fixed.model.building_superchain import BuildingSuperchain
from .base import BaseModel
from .region import Region


class RegionStartPos(BaseModel):
    campaign_code_name = peewee.CharField()
    region = peewee.ForeignKeyField(Region)

    port = peewee.BooleanField()
    province_capital = peewee.BooleanField()
    resource = EnumCharField(BuildingSuperchain, null=True)

    class Meta:
        indexes = (
            (('campaign_code_name', 'region'), True),
        )