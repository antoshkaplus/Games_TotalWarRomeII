import os
import pandas as pd
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

    building_culture_list = []
    for _, row in df.iterrows():
        ff = db.BuildingCulture(building_code_name=row['building'],
                                culture=row['culture'],
                                subculture=row['subculture'],
                                faction=row['faction'],
                                short_description=row['short_description'])
        building_culture_list.append(ff)

    db.BuildingCulture.bulk_create(building_culture_list)


insert_building_cultures()