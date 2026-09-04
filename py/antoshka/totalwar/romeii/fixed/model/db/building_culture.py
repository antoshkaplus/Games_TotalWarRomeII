import peewee
from .base import BaseModel


class BuildingCulture(BaseModel):
    building_code_name = peewee.CharField()
    culture = peewee.CharField()
    subculture = peewee.CharField(null=True)
    faction = peewee.CharField(null=True)
    short_description = peewee.CharField()

    # Sometimes building may be specialized somehow per particular faction.
    # And culture too. Slum is present in any culture.
    class Meta:
        indexes = (
            (('building_code_name', 'culture', 'subculture', 'faction'), True),
        )
