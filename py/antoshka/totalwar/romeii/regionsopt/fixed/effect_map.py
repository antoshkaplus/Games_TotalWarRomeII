import typing as ty
from antoshka.totalwar.romeii.common.serializable import Serializable
from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from ..stats import Stats


province_stats = {
    ('rom_building_gdp_agriculture_animal_husbandry', 'this_building'): 'wealth_livestock',
    ('rom_building_gdp_agriculture_farming', 'this_building'): 'wealth_farming',
    ('rom_building_gdp_culture_entertainment', 'this_building'): 'wealth_fun',
    ('rom_building_gdp_culture_learning', 'this_building'): 'wealth_learning',
    ('rom_building_gdp_industry_manufacture', 'this_building'): 'wealth_mnfr',
    ('rom_building_gdp_industry_mining', 'this_building') : 'wealth_mining',
    ('rom_building_gdp_subsistence', 'this_building'): 'wealth_subsistence',
    ('rom_building_gdp_trade_local', 'this_building'): 'wealth_local_com',
    ('rom_building_gdp_trade_sea', 'this_building'): 'wealth_mari_com',

    ('rom_building_gdp_mod_all', 'regions_in_this_province'): 'wealth_pct_all',
    ('rom_building_gdp_mod_agriculture_all', 'regions_in_this_province'): 'wealth_pct_agri',
    ('rom_building_gdp_mod_agriculture_farming', 'regions_in_this_province'): 'wealth_pct_farming',
    ('rom_building_gdp_mod_industry', 'regions_in_this_province'): 'wealth_pct_industry',
    ('rom_building_gdp_mod_industry_manufacturing', 'regions_in_this_province'): 'wealth_pct_mnfr',
    ('rom_building_gdp_mod_industry_mining', 'regions_in_this_province'): 'wealth_pct_mining',
    ('rom_building_gdp_mod_culture_entertainment', 'regions_in_this_province'): 'wealth_pct_fun',
    ('rom_building_gdp_mod_culture_all', 'regions_in_this_province'): 'wealth_pct_culture',
    ('rom_building_gdp_mod_trade_all', 'regions_in_this_province'): 'wealth_pct_com',

    ('rom_building_public_order_attitude_squalor', 'this_province'): 'order',
    ('rom_building_public_order_happiness', 'this_province'): 'order',
    ('rom_building_public_order_happiness_sanitation', 'this_province'): 'order',

    # Grain resource provides food per adjacent region + per region in province
    # hard to account for it. Can hardcode this or just remember about it.
    ('rom_building_food_farming_grain', 'this_region'): 'food',
    ('rom_building_food_reserves', 'this_region'): 'food',
    ('rom_building_food_trade', 'this_region'): 'food',
    ('rom_building_food_fishing', 'this_region'): 'food',

    ('rom_building_growth_all', 'this_province'): 'growth',

    ('rom_building_culture_conversion_balkan', 'this_region'): 'culture',

    ('rom_building_recruitment_points', 'this_province'): 'recruit_slots'
}

# Some values in database should flip sign with accordance to application.
province_negate_stats = {
    ('rom_building_food_consumption', 'this_region'): 'food',
}

# edict
# barb_religious_dacian_gebelizis_2 name:Grove of Gebeleizis
# rom_province_initiative_barbarian_tribute_mod_public_order this_province

# edict
# barb_religious_dacian_kotys_3 name:Shrine of Kotys
# rom_province_initiative_festival_mod_gdp_agriculture_mod

faction_stats = {
    ('rom_building_gdp_mod_agriculture_all', 'in_all_your_regions'): 'wealth_pct_agri',
    ('rom_building_gdp_mod_agriculture_all', 'this_province_faction_all_regions'): 'wealth_pct_agri',
    ('rom_building_gdp_mod_industry_mining', 'in_all_your_regions'): 'wealth_pct_mining',
    ('rom_building_gdp_mod_industry_manufacturing', 'in_all_your_regions'): 'wealth_pct_mnfr',
    ('rom_building_gdp_mod_trade_all', 'in_all_your_regions'): 'wealth_pct_com',

    ('rom_building_public_order_happiness_sanitation', 'in_all_your_provinces'): 'order',
    ('rom_building_public_order_happiness', 'in_all_your_provinces'): 'order',
    ('rom_building_public_order_happiness', 'this_province_faction_all_provinces'): 'order',

    ('rom_building_trade_tariffs_all', 'this_faction'): 'tariff_trade_agree_pct',
    ('rom_building_research_points', 'this_faction'): 'research_pct',

    ('rom_building_building_cost_mod', 'this_province_faction_all_regions'): 'build_cost_pct',
    ('rom_building_gdp_mod_culture_all', 'this_province_faction_all_regions'): 'wealth_pct_culture',
    ('rom_building_gdp_mod_trade_sea', 'this_province_faction_all_regions'):  'wealth_pct_mari_com',
    ('rom_building_tax_level', 'this_province_faction_all_provinces'): 'tax_pct',
    ('rom_building_recruitment_points_naval', 'this_province_faction_all_sea_regions'): 'recruit_slots_fleet',
    ('rom_building_trade_tariffs_all', 'this_province_faction'): 'tariff_trade_agree_pct',
    ('rom_building_research_points_mod_civil', 'this_province_faction'): 'research_pct_civil',
    # Negative value reduces penalty from foreign culture.
    ('rom_faction_public_order_foreign_culture_penalty', 'this_province_faction_all_provinces'): 'order_pct_foreign_culture',
    ('rom_building_research_points_mod_military', 'this_province_faction'): 'research_pct_military',
    ('rom_province_growth_province_effects', 'this_province_faction_all_provinces'): 'growth',
    ('rom_force_unit_mod_morale', 'this_province_faction_all_armies'): 'morale_army',
    ('rom_force_unit_mod_morale', 'this_province_faction_all_forces'): 'morale',
    ('rom_province_initiative_festival_mod_happiness_entertainment', 'this_province_faction_all_provinces'): '',
    ('rom_province_initiative_festival_mod_gdp_entertainment_mod', 'this_province_faction_all_provinces'): '',
    ('rom_force_unit_mod_bows_missile_range', 'this_province_faction_all_forces'): 'bow_range_pct',
    ('rom_building_culture_conversion_to_state_culture', 'this_province_faction'): 'culture',

    # Positive value reduces order penalty when occupying foreign lands.
    ('rom_faction_trait_successor_core_alexander_legacy', 'this_faction'): 'order_pct_occupation',

    # Baktria
    ('rom_faction_trait_successor_baktria_silk_road', 'in_all_your_regions_unseen'): 'wealth_pct_com',
    ('rom_faction_trait_eastern_parthia_multiculturalism', 'in_all_your_provinces_unseen'): 'order_pct_foreign_culture',
    # Iceni
    ('rom_faction_trait_britannic_iceni_pastoral_ways', 'in_all_your_regions_unseen'): 'wealth_pct_agri'
}


class ProvinceFactionStats(Serializable):
    def __init__(self):
        self.province_stats = Stats()
        self.faction_stats = Stats()

    def __iadd__(self, other: ProvinceFactionStats):
        self.province_stats += other.province_stats
        self.faction_stats += other.faction_stats
        return self

    def __add__(self, other: ProvinceFactionStats):
        res = ProvinceFactionStats()
        res.province_stats = self.province_stats + other.province_stats
        res.faction_stats = self.faction_stats + other.faction_stats
        return res

    def to_serializable(self):
        obj = {}
        if not self.province_stats.empty:
            obj['province'] = self.province_stats.to_serializable()
        if not self.faction_stats.empty:
            obj['faction'] = self.faction_stats.to_serializable()
        return obj

    @staticmethod
    def from_serializable(obj) -> ProvinceFactionStats:
        res = ProvinceFactionStats()
        if 'province' in obj:
            res.province_stats = Stats.from_serializable(obj['province'])
        if 'faction' in obj:
            res.faction_stats = Stats.from_serializable(obj['faction'])
        return res


def effects_to_stats(effects: ty.Iterable[ty.Union[fixed_db.RegionEffects, fixed_db.BuildingEffect, fixed_db.FactionEffect]]) -> ProvinceFactionStats:
    global province_stats
    global faction_stats

    res = ProvinceFactionStats()
    for e_ in effects:
        pair = (e_.effect_name, e_.scope)
        if pair in province_stats:
            stat_name = province_stats[pair]
            res.province_stats += Stats({stat_name: e_.value})

        if pair in province_negate_stats:
            stat_name = province_negate_stats[pair]
            res.province_stats += Stats({stat_name: -e_.value})

        if pair in faction_stats:
            stat_name = faction_stats[pair]
            res.faction_stats += Stats({stat_name: e_.value})
    return res