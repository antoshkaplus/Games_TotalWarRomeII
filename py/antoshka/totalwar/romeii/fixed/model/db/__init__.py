from .base import DB
from .building_effects import BuildingEffect
from .building_upgrade import BuildingUpgrade
from .faction import Faction
from .building_culture import BuildingCulture
from .building_culture_screen import BuildingCultureScreen
from .province import Province
from .building import Building
from .region import Region
from .region_effects import RegionEffects
from .region_start_pos import RegionStartPos
from .building_chain_availability import BuildingChainAvailability
from .faction_effects import FactionEffect, add_faction_effect_index
from .technology import Technology
from .building_technology import BuildingTechnology
from .technology_node_set import TechnologyNodeSet
from .technology_node import TechnologyNode


def make_tables():
    add_faction_effect_index()
    DB.create_tables([BuildingEffect, BuildingUpgrade, Faction,
                      BuildingCulture, BuildingCultureScreen, Building,
                      Province, Region, RegionEffects, RegionStartPos,
                      BuildingChainAvailability, FactionEffect,
                      Technology, BuildingTechnology, TechnologyNodeSet,
                      TechnologyNode])
