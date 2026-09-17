import peewee
from .base import BaseModel


class BuildingChainAvailability(BaseModel):
    chain = peewee.CharField()
    culture = peewee.CharField(null=True)
    subculture = peewee.CharField(null=True)
    faction = peewee.CharField(null=True)
    campaign = peewee.CharField(null=True)

    class Meta:
        indexes = (
            (('chain', 'culture', 'subculture', 'faction', 'campaign'), True),
        )

