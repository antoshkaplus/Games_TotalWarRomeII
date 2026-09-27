import typing as ty
from antoshka.totalwar.romeii.fixed.model.campaign_name import CampaignName, CAMPAIGN_NAME_TO_CODE
from antoshka.totalwar.romeii.fixed.model import db as fixed_db


type FactionCodeName = str


def list_faction_technology_sets(faction_code_name: FactionCodeName,
                                 campaign_name: CampaignName = CampaignName.Grand) -> ty.List[fixed_db.TechnologyNodeSet]:
    campaign_code = CAMPAIGN_NAME_TO_CODE[campaign_name]
    faction = fixed_db.Faction.get_by_id(faction_code_name)

    categories = list(fixed_db.TechnologyNodeSet.select(fixed_db.TechnologyNodeSet.category).distinct())
    categories = set(c_.category for c_ in categories)

    campaign_condition = (fixed_db.TechnologyNodeSet.campaign_code_name == campaign_code) | (fixed_db.TechnologyNodeSet.campaign_code_name.is_null())
    faction_condition = (fixed_db.TechnologyNodeSet.faction == faction.code_name) | (fixed_db.TechnologyNodeSet.faction.is_null())
    culture_condition = (fixed_db.TechnologyNodeSet.culture == faction.culture) | (fixed_db.TechnologyNodeSet.culture.is_null())
    subculture_condition = (fixed_db.TechnologyNodeSet.subculture == faction.subculture) | (fixed_db.TechnologyNodeSet.subculture.is_null())

    faction_node_sets = list(fixed_db.TechnologyNodeSet.select().where(
        fixed_db.TechnologyNodeSet.category.in_(categories) & (fixed_db.TechnologyNodeSet.faction == faction.code_name),
        campaign_condition, culture_condition, subculture_condition))
    for f_ in faction_node_sets:
        categories.discard(f_.category)

    subculture_node_sets = list(fixed_db.TechnologyNodeSet.select().where(
        fixed_db.TechnologyNodeSet.category.in_(categories) & (fixed_db.TechnologyNodeSet.subculture == faction.subculture),
        campaign_condition, faction_condition, culture_condition))
    for f_ in subculture_node_sets:
        categories.discard(f_.category)

    if len(categories) != 0:
        raise RuntimeError(f'Categories {categories} not assigned.')

    tech_node_sets = []
    tech_node_sets.extend(faction_node_sets)
    tech_node_sets.extend(subculture_node_sets)

    return tech_node_sets


def list_faction_technologies(faction_code_name: FactionCodeName,
                              campaign_name: CampaignName = CampaignName.Grand) -> ty.Set[fixed_db.Technology]:
    tech_sets = list_faction_technology_sets(faction_code_name, campaign_name)
    nodes = fixed_db.TechnologyNode.select().join(fixed_db.Technology).where(fixed_db.TechnologyNode.technology_node_set.in_(tech_sets))
    return [n_.technology for n_ in nodes]