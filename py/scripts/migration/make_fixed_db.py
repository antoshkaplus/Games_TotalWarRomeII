import typing as ty
import os
import json
import argparse
import pandas as pd
import numpy as np
from antoshka.totalwar.romeii.view.cli.parser_util import add_parser
from antoshka.totalwar.romeii.fixed.model.building_superchain import BuildingSuperchain
from antoshka.totalwar.romeii.fixed.model import db
from antoshka.totalwar.romeii import json_util
from antoshka.config import get_fixed_db_path


root_path = os.path.dirname(get_fixed_db_path())
db.DB.init(get_fixed_db_path())
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
                        # In reality this is diplomacy culture. But should be the same.
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


def insert_province():
    path = os.path.join(root_path, 'fixed/provinces.loc.tsv')
    df = pd.read_csv(path, sep='\t', comment='#')
    df['key'] = df['key'].str.removeprefix('provinces_onscreen_')

    item_list = []
    for _, row in df.iterrows():
        ff = db.Province(code_name=row['key'],
                         province_name=row['text'])
        item_list.append(ff)
    db.Province.bulk_create(item_list)


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


def insert_regions():
    path = os.path.join(root_path, 'fixed/regions.loc.tsv')
    df_settlement_name = pd.read_csv(path, sep='\t', comment='#')
    df_settlement_name = df_settlement_name[df_settlement_name['key'].str.startswith('regions_onscreen_')]
    df_settlement_name['key'] = df_settlement_name['key'].str.removeprefix('regions_onscreen_')
    settlement_name = {row['key']: row['text'] for _, row in df_settlement_name.iterrows()}

    path = os.path.join(root_path, 'fixed/region_to_province_junctions.tsv')
    df_province = pd.read_csv(path, sep='\t', comment='#')

    provinces = {item.code_name: item for item in db.Province.select()}

    item_list = []
    for _, row in df_province.iterrows():
        item = db.Region(code_name=row['region'],
                         province=provinces[row['province']],
                         settlement_name=settlement_name[row['region']])
        item_list.append(item)
    db.Region.bulk_create(item_list)


def insert_region_start_pos_1():
    path = os.path.join(root_path, 'fixed/start_pos_region_slot_templates.tsv')
    df = pd.read_csv(path, sep='\t', comment='#')

    regions = {item.code_name: item for item in db.Region.select()}

    item_list = []
    for idx, region_df in df.groupby(['campaign', 'region']):
        campaign = idx[0]
        region = idx[1]
        port = False
        province_capital = False
        for _, row in region_df.iterrows():
            if row['slot_template'] == 'port':
                port = True
            if row['slot_template'].startswith('major'):
                province_capital = True
        item = db.RegionStartPos(campaign_code_name=campaign,
                                 region=regions[region],
                                 port=port,
                                 province_capital=province_capital)
        item_list.append(item)
    db.RegionStartPos.bulk_create(item_list)


def insert_region_start_pos_2():
    """
    Requires startpos.esf file parsed into json per campaign
    """
    building_superchain = {item.code_name: BuildingSuperchain.parse(item.superchain)
                           for item in db.Building.select()
                           if item.superchain in set(BuildingSuperchain)}

    region_start_pos = {(item.campaign_code_name, item.region.code_name): item
                        for item in db.RegionStartPos.select()}

    save_region_start_pos = []
    campaigns = ['main_rome']
    for cc in campaigns:
        path = os.path.join(root_path, f'fixed/startpos_{cc}.json')
        with open(path, 'r') as file:
            obj = json.load(file)
        regions_path = ('CAMPAIGN_STARTPOS/[]/CAMPAIGN_STARTPOS/[]/CAMPAIGN_ENV/[]/'
                        'CAMPAIGN_MODEL/[]/WORLD/[]/REGION_MANAGER/[]/REGIONS_ARRAY/[]/[]/REGION')
        regions_obj = json_util.go_to(obj, regions_path)
        for idx, item in enumerate(regions_obj):
            region_code_name = item[1]
            buildings_path = '[]/REGION_SLOT_MANAGER/[]/REGION_SLOT_ARRAY/[]/[]/REGION_SLOT/[]/BUILDING_MANAGER/[]/BUILDING'
            buildings_obj = json_util.go_to_list(item, buildings_path)

            building_code_name = buildings_obj[3]
            start_pos_key = (cc, region_code_name)
            if building_superchain[building_code_name].resource_kind and start_pos_key in region_start_pos:
                region_start_pos[start_pos_key].resource = building_superchain[building_code_name]
                save_region_start_pos.append(region_start_pos[start_pos_key])

    with db.DB.atomic():
        for item in save_region_start_pos:
            item.save(only=[db.RegionStartPos.resource])


def insert_region_start_pos_all(_):
    insert_region_start_pos_1()
    insert_region_start_pos_2()


def insert_region_effects(_):
    path = os.path.join(root_path, 'fixed/regions.tsv')
    df = pd.read_csv(path, sep='\t', comment='#')
    df = df.replace({np.nan: None})

    effect_bundle_region = {}
    for _, row in df.iterrows():
        if row['owner_bundle']:
            effect_bundle_region[ row['owner_bundle'] ] = row['key']

    item_list = []

    path = os.path.join(root_path, 'fixed/effect_bundles_to_effects_junctions.tsv')
    df = pd.read_csv(path, sep='\t', comment='#')
    df['value'] = df['value'].astype(int)
    for _, row in df.iterrows():
        if row['effect_bundle_key'] in effect_bundle_region:
            regon_code_name = effect_bundle_region[row['effect_bundle_key']]
            item = db.RegionEffects(
                region=db.Region(code_name=regon_code_name),
                effect_bundle=row['effect_bundle_key'],
                effect_name=row['effect_key'],
                scope=row['effect_scope'],
                value=row['value'])
            item_list.append(item)

    db.RegionEffects.bulk_create(item_list)


def insert_building_chain_availability(_):
    path = os.path.join(root_path, 'fixed/building_chain_availability_sets.tsv')
    df_sets = pd.read_csv(path, sep='\t', comment='#')

    path = os.path.join(root_path, 'fixed/building_chain_availabilities.tsv')
    df = pd.read_csv(path, sep='\t', comment='#')

    df = pd.merge(df, df_sets, how='left', left_on='set_id', right_on='id')
    df = df[['building_chain', 'culture', 'faction', 'sub_culture', 'campaign']]
    df = df.replace({np.nan: None})

    item_list = []
    for row in df.to_records():
        item = {
            'chain': row['building_chain'],
            'culture': row['culture'],
            'subculture': row['sub_culture'],
            'faction': row['faction'],
            'campaign': row['campaign']
        }
        item_list.append(item)

    db.BuildingChainAvailability.insert_many(item_list).on_conflict_ignore().execute()


parser = argparse.ArgumentParser(description='Save file db')
sps = parser.add_subparsers()

add_parser(sps, 'insert-region-start-pos', func=insert_region_start_pos_all)
add_parser(sps, 'insert-region-effects', func=insert_region_effects)
add_parser(sps, 'insert-chain-availability', func=insert_building_chain_availability)

args = parser.parse_args()
args.func(args)


