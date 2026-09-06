import peewee
from .base import BaseModel
from .region import Region


class RegionBuildingSlot(BaseModel):
    region = peewee.ForeignKeyField(Region, backref='building_slots')
    building_code_name = peewee.CharField(null=True)
    faction_code_name = peewee.CharField(null=True)
    slot_idx = peewee.IntegerField()
    slot_type = peewee.CharField()

    class Meta:
        indexes = (
            (('region', 'slot_idx'), True),
        )