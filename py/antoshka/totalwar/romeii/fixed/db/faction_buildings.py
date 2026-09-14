import typing as ty
from antoshka.totalwar.romeii.campaign_name import CampaignName
from antoshka.totalwar.romeii.fixed.model import db as fixed_db


type BuildingCodeName = str
type FactionCodeName = str


def list_faction_buildings(faction_code_name: FactionCodeName,
                           campaign_type: CampaignName = CampaignName.Grand) -> ty.Set[BuildingCodeName]:
    """
    faction_code_name = 'rom_getae'
    religious_flavor = 'dacian'
    campaign_type = CampaignType.Grand
    """
    religious_flavor = None
    if faction_code_name == 'rom_getae':
        religious_flavor = 'dacian'

    faction = fixed_db.Faction.get_by_id(faction_code_name)
    building_culture_list = list(fixed_db.BuildingCulture.select().where(
        (~fixed_db.BuildingCulture.building_code_name.startswith('rom_ALL')) &
        (~fixed_db.BuildingCulture.building_code_name.startswith('rom_BARBARIAN')) &
        (~fixed_db.BuildingCulture.building_code_name.startswith('3c_')) &
        (~fixed_db.BuildingCulture.building_code_name.startswith('pel_')) &
        (~fixed_db.BuildingCulture.building_code_name.startswith('inv_')) &
        (fixed_db.BuildingCulture.culture == faction.culture) &
        (fixed_db.BuildingCulture.subculture.is_null() | (fixed_db.BuildingCulture.subculture == faction.subculture)) &
        (fixed_db.BuildingCulture.faction.is_null() | (fixed_db.BuildingCulture.faction == faction.code_name))))

    building_culture_list = list(filter(lambda b: (not '_religious_' in b.building_code_name)
                                                  or (religious_flavor in b.building_code_name),
                                        building_culture_list))
    building_culture_list = list(filter(lambda b: '_nomad_' not in b.building_code_name,
                                        building_culture_list))
    building_culture_list = list(filter(lambda b: '_slum' not in b.building_code_name,
                                        building_culture_list))

    building_code_names = set(b.building_code_name for b in building_culture_list)
    return building_code_names