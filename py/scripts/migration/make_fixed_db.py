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


insert_building_upgrades()