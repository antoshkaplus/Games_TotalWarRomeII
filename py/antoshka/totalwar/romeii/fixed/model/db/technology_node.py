import peewee
from .base import BaseModel
from .technology import Technology
from .technology_node_set import TechnologyNodeSet


class TechnologyNode(BaseModel):
    code_name = peewee.CharField(primary_key=True)
    campaign_code_name = peewee.CharField(null=True)
    faction = peewee.CharField(null=True)
    technology = peewee.ForeignKeyField(Technology)
    technology_node_set = peewee.ForeignKeyField(TechnologyNodeSet)
