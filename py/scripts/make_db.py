import os
import json
from antoshka.totalwar.romeii.model import db, Faction
from antoshka.totalwar.romeii.model.db import Region

root_path = '/home/antoshkaplus/Documents/Games_TotalWarRomeII/tmp/my_auto_save_legendary'
db_path = os.path.join(root_path, 'my_auto_save_legendary.db')

db.DB.init(db_path)
db.make_tables()


def insert_factions():
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


def insert_provinces():
    with open(os.path.join(root_path, 'my_auto_save_legendary-provinces.json')) as fp:
        provinces_obj = json.load(fp)
    with db.DB.atomic():
        for entry in provinces_obj:
            db.Province.create(code_name=entry['id'])


def insert_regions():
    with open(os.path.join(root_path, 'my_auto_save_legendary-provinces.json')) as fp:
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


insert_regions()




