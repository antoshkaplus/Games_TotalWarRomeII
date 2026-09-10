import argparse
from collections import defaultdict
from antoshka.totalwar.romeii.fixed.model import db as fixed_db


db_path = "/home/antoshkaplus/Documents/Games_TotalWarRomeII/data_lfs/fixed.db"
fixed_db.DB.init(db_path)


faction_code_name = 'rom_getae'
religious_flavor = 'dacian'

faction = fixed_db.Faction.get_by_id(faction_code_name)
print(faction.code_name)
print(faction.culture)
print(faction.subculture)
print(faction.screen_name)


building_culture_list = list(fixed_db.BuildingCulture.select().where(
    (~fixed_db.BuildingCulture.building_code_name.startswith('rom_ALL')) &
    (~fixed_db.BuildingCulture.building_code_name.startswith('rom_BARBARIAN')) &
    (~fixed_db.BuildingCulture.building_code_name.startswith('3c_')) &
    (~fixed_db.BuildingCulture.building_code_name.startswith('pel_')) &
    (~fixed_db.BuildingCulture.building_code_name.startswith('inv_')) &
    (fixed_db.BuildingCulture.culture == faction.culture) &
    (fixed_db.BuildingCulture.subculture.is_null() | (fixed_db.BuildingCulture.subculture == faction.subculture)) &
    (fixed_db.BuildingCulture.faction.is_null() | (fixed_db.BuildingCulture.faction == faction.code_name))))

building_culture_list = list(filter(lambda b: (not '_religious_' in b.building_code_name) or religious_flavor in b.building_code_name, building_culture_list))
building_culture_list = list(filter(lambda b: '_nomad_' not in b.building_code_name, building_culture_list))
building_code_names = set(b.building_code_name for b in building_culture_list)

building_effects = defaultdict(list)
for be in fixed_db.BuildingEffect.select():
    if be.code_name in building_code_names:
        building_effects[be.code_name].append(be)

buildings = {}
for bb in fixed_db.Building.select():
    if bb.code_name in building_code_names:
        buildings[bb.code_name] = bb


parser = argparse.ArgumentParser(description='Faction buildings CLI')
parser.add_argument('--effects', action='store_true')
parser.add_argument('--culture', action='store_true')
parser.add_argument('--definition', action='store_true')
args = parser.parse_args()


building_culture_list = sorted(building_culture_list, key=lambda b: b.building_code_name)
for bc in building_culture_list:
    print(bc.building_code_name + f' name:' + bc.screen.get().building_name)
    if args.culture:
        s = 'culture: ' + bc.culture
        if bc.subculture:
            s += ' subculture: ' + bc.subculture
        if bc.faction:
            s += ' faction: ' + bc.faction
        print('  ' + s)
    if args.effects:
        print('  effects:')
        for be in building_effects[bc.building_code_name]:
            print('   ', be.effect_name, be.scope, be.value)
    if args.definition:
        bb = buildings[bc.building_code_name]
        s = f'  def: {bb.superchain} lv:{bb.level} turns:{bb.create_turns} cost:{bb.create_cost}'
        if bb.resource_requirement:
            s += ' ' + bb.resource_requirement
        print(s)
