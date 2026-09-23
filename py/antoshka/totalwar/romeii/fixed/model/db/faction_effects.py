import peewee
from .base import BaseModel
from .faction import Faction


class FactionEffect(BaseModel):
    faction = peewee.ForeignKeyField(Faction, backref='effects')
    # Can be null in case of effects related regardless political party.
    # Do not add records for non-playable political parties.
    political_party = peewee.CharField(null=True)
    # Effect bundle does not play a role, but is kept for reference.
    effect_bundle = peewee.CharField()

    effect_name = peewee.CharField()
    scope = peewee.CharField()
    value = peewee.IntegerField()


def add_faction_effect_index():
    idx = FactionEffect.index(FactionEffect.faction,
                              peewee.fn.COALESCE(FactionEffect.political_party, ''),
                              FactionEffect.effect_name,
                              unique=True)
    FactionEffect.add_index(idx)