import os
import json
import argparse
import pathlib
from antoshka.view.cli import add_parser
from antoshka.totalwar.romeii.model import db, Faction
from antoshka.totalwar.romeii.model.db import Region
from antoshka.totalwar.romeii import json_util


def init_db(db_path: str | pathlib.Path):
    if db.DB.database is None:
        db.DB.init(str(db_path))
    db.make_tables()


def insert_factions(args):
    root_path = os.path.dirname(args.save_path)
    init_db(pathlib.Path(args.save_path).with_suffix('.db'))

    faction_list = []
    factions_path = os.path.join(root_path, 'factions')
    entries = os.listdir(factions_path)
    for faction_filename in entries:
        with open(os.path.join(factions_path, faction_filename)) as fp:
            faction_obj = json.load(fp)
        faction_obj = faction_obj[0]['Nodes']
        faction_id = faction_obj[0]
        faction_code_name = faction_obj[2]['Nodes'][1]

        faction_list.append(Faction(faction_id, faction_code_name))


    faction_list = [db.Faction(id=fn.id, code_name=fn.code_name)
                    for fn in faction_list]
    db.Faction.bulk_create(faction_list)


def insert_provinces(args):
    init_db(pathlib.Path(args.save_path).with_suffix('.db'))

    with open(args.save_path.replace('.save', '-provinces.json')) as fp:
        provinces_obj = json.load(fp)
    with db.DB.atomic():
        for entry in provinces_obj:
            db.Province.create(code_name=entry['id'])


def insert_regions(args):
    root_path = os.path.dirname(args.save_path)
    init_db(pathlib.Path(args.save_path).with_suffix('.db'))

    with open(args.save_path.replace('.save', '-provinces.json')) as fp:
        provinces_obj = json.load(fp)
    region_province = {region_code_name: province['id']
                       for province in provinces_obj
                       for region_code_name in province['region_ids']}
    region_capital = {region_code_name: province['capital_region_id'] == region_code_name
                      for province in provinces_obj
                      for region_code_name in province['region_ids']}

    region_list = []
    regions_path = os.path.join(root_path, 'regions')
    entries = os.listdir(regions_path)
    for region_filename in entries:
        with open(os.path.join(regions_path, region_filename)) as fp:
            region_obj = json.load(fp)
        region_obj = region_obj[0]['Nodes']
        region_id = region_obj[0]
        region_code_name = region_obj[1]
        region_owner_id = region_obj[14]

        region_list.append(Region(id=region_id,
                                  code_name=region_code_name,
                                  province=db.Province(code_name=region_province[region_code_name]),
                                  province_capital=region_capital[region_code_name],
                                  owner=db.Faction(id=region_owner_id)))
    db.Region.bulk_create(region_list)


def insert_province_religions(args):
    root_path = os.path.dirname(args.save_path)
    init_db(pathlib.Path(args.save_path).with_suffix('.db'))

    # Non province capital regions have garbage values.
    region_religions = {}
    regions_path = os.path.join(root_path, 'regions')
    entries = os.listdir(regions_path)
    for region_filename in entries:
        with open(os.path.join(regions_path, region_filename)) as fp:
            region_obj = json.load(fp)

        region_code_name = json_util.go_to(region_obj, '[]/REGION') [1]
        religions = json_util.go_to(region_obj, '[]/REGION/[]/POPULATION/[]/REGION_FACTORS/[]/RELIGION_BREAKDOWN')

        region_religions[region_code_name] = religions

    province_religion_list = []
    for pr in list(db.Province.select()):
        for rg in pr.regions:
            rg: db.Region
            if not rg.province_capital:
                continue

            for religion_code_name, ratio in region_religions[rg.code_name]:
                if ratio == 0.:
                    continue
                province_religion_list.append(
                    db.ProvinceReligion(province=pr, religion_code_name=religion_code_name, ratio=ratio))

    db.ProvinceReligion.bulk_create(province_religion_list)


def insert_all(args):
    init_db(pathlib.Path(args.save_path).with_suffix('.db'))

    with db.DB.atomic():
        insert_factions(args)
        insert_provinces(args)
        insert_regions(args)
        insert_province_religions(args)


parser = argparse.ArgumentParser(description='Save file db')
sps = parser.add_subparsers()

p = add_parser(sps, 'insert-factions', func=insert_factions)
p.add_argument('save_path', type=str)

p = add_parser(sps, 'insert-provinces', func=insert_provinces)
p.add_argument('save_path', type=str)

p = add_parser(sps, 'insert-regions', func=insert_regions)
p.add_argument('save_path', type=str)

p = add_parser(sps, 'insert-religions', func=insert_province_religions)
p.add_argument('save_path', type=str)

p = add_parser(sps, 'insert-all', func=insert_all)
p.add_argument('save_path', type=str)

args = parser.parse_args()
args.func(args)



