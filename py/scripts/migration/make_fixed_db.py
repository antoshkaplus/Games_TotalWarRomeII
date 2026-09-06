import os
import pandas as pd
import numpy as np
from antoshka.totalwar.romeii.fixed.model import db


root_path = '/home/antoshkaplus/Documents/Games_TotalWarRomeII/data_lfs/'
db_path = os.path.join(root_path, 'fixed.db')

db.DB.init(db_path)
db.make_tables()


def insert_building_effects():
    path = os.path.join(root_path, 'fixed/building_effects_junction.tsv')
    df = pd.read_csv(path, sep='\t', comment='#')
    df['value'] = df['value'].astype(int)
    df['value_damaged'] = df['value_damaged'].astype(int)
    df['value_ruined'] = df['value_ruined'].astype(int)

    building_effects_list = []
    for _, row in df.iterrows():
        be = db.BuildingEffect(code_name=row['building'], effect_name=row['effect'],
                          scope=row['effect_scope'], value=row['value'],
                          value_damaged=row['value_damaged'], value_ruined=row['value_ruined'])
        building_effects_list.append(be)

    db.BuildingEffect.bulk_create(building_effects_list)


def insert_building_upgrades():
    path = os.path.join(root_path, 'fixed/building_upgrades_junction.tsv')
    df = pd.read_csv(path, sep='\t', comment='#')

    building_upgrades_list = []
    for _, row in df.iterrows():
        bu = db.BuildingUpgrade(from_code_name=row['from'], to_code_name=row['to'])
        building_upgrades_list.append(bu)

    db.BuildingUpgrade.bulk_create(building_upgrades_list)


def insert_factions():
    path = os.path.join(root_path, 'fixed/factions.tsv')
    df = pd.read_csv(path, sep='\t', comment='#')

    faction_list = []
    for _, row in df.iterrows():
        ff = db.Faction(code_name=row['key'],
                        culture=row['diplomacy_culture'],
                        subculture=row['subculture'],
                        screen_name=row['screen_name'])
        faction_list.append(ff)

    db.Faction.bulk_create(faction_list)


def insert_building_cultures():
    path = os.path.join(root_path, 'fixed/building_culture_variants.tsv')
    df = pd.read_csv(path, sep='\t', comment='#')
    df = df.replace({np.nan: None})

    building_culture_list = []
    for _, row in df.iterrows():
        ff = db.BuildingCulture(building_code_name=row['building'],
                                culture=row['culture'],
                                subculture=row['subculture'],
                                faction=row['faction'],
                                short_description=row['short_description'])
        building_culture_list.append(ff)

    db.BuildingCulture.bulk_create(building_culture_list)


def insert_building_culture_screen():
    path = os.path.join(root_path, 'fixed/building_culture_variants.loc.tsv')
    building_name_df = pd.read_csv(path, sep='\t', comment='#')
    building_name_df['key'] = building_name_df['key'].astype(str).str.removeprefix('building_culture_variants_name_')
    building_name_dict = {row['key']: row['text'] for _, row in building_name_df.iterrows()}

    path = os.path.join(root_path, 'fixed/building_short_description_texts.loc.tsv')
    description_df = pd.read_csv(path, sep='\t', comment='#')
    description_df['key'] = description_df['key'].astype(str).str.removeprefix('building_short_description_texts_short_description_')
    description_dict = {row['key']: row['text'] for _, row in description_df.iterrows()}

    with db.DB.atomic():
        item_list = []

        for bc in db.BuildingCulture.select():
            building_name_key = bc.building_code_name
            if bc.culture: building_name_key += bc.culture
            if bc.subculture: building_name_key += bc.subculture
            if bc.faction: building_name_key += bc.faction

            item = db.BuildingCultureScreen(
                building_culture=bc,
                building_name=building_name_dict[building_name_key],
                short_description=description_dict[bc.short_description])
            item_list.append(item)
        db.BuildingCultureScreen.bulk_create(item_list)


def insert_province_screen():
    path = os.path.join(root_path, 'fixed/provinces.loc.tsv')
    df = pd.read_csv(path, sep='\t', comment='#')
    df['key'] = df['key'].str.removeprefix('provinces_onscreen_')

    item_list = []
    for _, row in df.iterrows():
        ff = db.ProvinceScreen(province_code_name=row['key'],
                               province_name=row['text'])
        item_list.append(ff)
    db.ProvinceScreen.bulk_create(item_list)


def insert_region_screen():
    path = os.path.join(root_path, 'fixed/regions.loc.tsv')
    df = pd.read_csv(path, sep='\t', comment='#')
    df = df[df['key'].str.startswith('regions_onscreen_')]
    df['key'] = df['key'].str.removeprefix('regions_onscreen_')

    item_list = []
    for _, row in df.iterrows():
        ff = db.RegionScreen(region_code_name=row['key'],
                             settlement_name=row['text'])
        item_list.append(ff)
    db.RegionScreen.bulk_create(item_list)


def insert_buildings():
    path = os.path.join(root_path, 'fixed/building_levels.tsv')
    df_levels = pd.read_csv(path, sep='\t', comment='#')
    df_levels = df_levels[['level_name', 'chain', 'level', 'create_time', 'create_cost', 'resource_requirement']]

    path = os.path.join(root_path, 'fixed/building_chains.tsv')
    df_chains = pd.read_csv(path, sep='\t', comment='#')
    df_chains = df_chains[['key', 'building_superchain']]

    df = pd.merge(df_levels, df_chains,  how='left', left_on='chain', right_on='key')
    df = df.replace({np.nan: None})

    item_list = []
    for _, row in df.iterrows():
        ff = db.Building(code_name=row['level_name'],
                         chain=row['chain'],
                         superchain=row['building_superchain'],
                         level=row['level'],
                         create_turns=row['create_time'],
                         create_cost=row['create_cost'],
                         resource_requirement=row['resource_requirement'])
        item_list.append(ff)
    db.Building.bulk_create(item_list)


insert_buildings()