import typing as ty
from antoshka.totalwar.romeii.fixed.model.campaign_name import CampaignName, CAMPAIGN_NAME_TO_CODE
from antoshka.totalwar.romeii.fixed.model import db as fixed_db


type BuildingCodeName = str
type BuildingName = str
type BuildingChain = str
type FactionCodeName = str


def list_faction_chains(faction_code_name: FactionCodeName,
                        campaign_name: CampaignName = CampaignName.Grand) -> ty.Set[BuildingChain]:
    faction = fixed_db.Faction.get_by_id(faction_code_name)
    conditions = [fixed_db.BuildingChainAvailability.culture == faction.culture]
    faction_present = fixed_db.BuildingChainAvailability.select().where(fixed_db.BuildingChainAvailability.faction == faction.code_name).exists()
    if faction_present:
        conditions.append(fixed_db.BuildingChainAvailability.faction == faction.code_name)
    else:
        conditions.append(fixed_db.BuildingChainAvailability.faction.is_null())

    subculture_present = fixed_db.BuildingChainAvailability.select().where(fixed_db.BuildingChainAvailability.subculture == faction.subculture).exists()
    if subculture_present:
        conditions.append(fixed_db.BuildingChainAvailability.subculture == faction.subculture)
    else:
        conditions.append(fixed_db.BuildingChainAvailability.subculture.is_null())

    campaign_code = CAMPAIGN_NAME_TO_CODE[campaign_name]
    campaign_present = fixed_db.BuildingChainAvailability.select().where(fixed_db.BuildingChainAvailability.campaign == campaign_code).exists()
    if campaign_present:
        conditions.append(fixed_db.BuildingChainAvailability.campaign == campaign_code)
    else:
        conditions.append(fixed_db.BuildingChainAvailability.campaign.is_null())

    res = fixed_db.BuildingChainAvailability.select().where(*conditions)
    res = [r_.chain for r_ in res]

    if campaign_name == CampaignName.Grand:
        res = [r_ for r_ in res if not r_.startswith(('rom_BARBARIAN', 'rom_ALL', 'rom_HELLENIC'))]
    return set(res)


def list_faction_buildings_names(faction_code_name: FactionCodeName,
                                 campaign_name: CampaignName = CampaignName.Grand) -> ty.Dict[BuildingCodeName, BuildingName]:

    faction_chains = list_faction_chains(faction_code_name, campaign_name)
    res = fixed_db.Building.select().where(fixed_db.Building.chain.in_(faction_chains))
    building_code_names = set(r_.code_name for r_ in res)

    faction = fixed_db.Faction.get_by_id(faction_code_name)
    res = fixed_db.BuildingCulture.select().join(fixed_db.BuildingCultureScreen).where(
        fixed_db.BuildingCulture.building_code_name.in_(building_code_names) &
        (fixed_db.BuildingCulture.culture.is_null() | (fixed_db.BuildingCulture.culture == faction.culture)) &
        (fixed_db.BuildingCulture.subculture.is_null() | (fixed_db.BuildingCulture.subculture == faction.subculture)) &
        (fixed_db.BuildingCulture.faction.is_null() | (fixed_db.BuildingCulture.faction == faction_code_name)))
    building_names = {r_.building_code_name: r_.screen.get().building_name for r_ in res}
    return building_names


def list_faction_buildings(faction_code_name: FactionCodeName,
                           campaign_name: CampaignName = CampaignName.Grand) -> ty.Set[BuildingCodeName]:
    return set(list_faction_buildings_names(faction_code_name, campaign_name))