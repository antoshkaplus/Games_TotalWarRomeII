import peewee
from .base import BaseModel


class Faction(BaseModel):
    code_name = peewee.CharField(primary_key=True)
    # `diplomacy_culture` in `factions.tsv`, but it is the same
    # following table `cultures_subcultures`
    culture = peewee.CharField()
    subculture = peewee.CharField()
    screen_name = peewee.CharField()


