import typing as ty
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
}


class _ProvinceFactionStats:
    def __init__(self):
        self.province_stats = Stats()
        self.faction_stats = Stats()


def effects_to_stats(effects: ty.Iterable[ty.Union[fixed_db.RegionEffects, fixed_db.BuildingEffect]]):
    res = _ProvinceFactionStats()
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