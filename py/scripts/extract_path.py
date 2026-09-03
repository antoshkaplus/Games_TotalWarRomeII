import json
from antoshka.totalwar.romeii import json_util

root_path = '/home/antoshkaplus/Documents/Games_TotalWarRomeII/tmp/my_auto_save_legendary/'
json_filename = 'my_auto_save_legendary_dup.json'

# extract_path = 'CAMPAIGN_SAVE_GAME/[]/SAVE_GAME_HEADER'
# extract_path = 'CAMPAIGN_SAVE_GAME/[]/CAMPAIGN_SAVE_GAME/[]/SAVE_GAME_HEADER'
extract_path = ("CAMPAIGN_SAVE_GAME/[]/CAMPAIGN_SAVE_GAME/[]/"
                "CAMPAIGN_ENV/[]/CAMPAIGN_MODEL/[]/WORLD/[]/"
                "REGION_MANAGER/[]/REGIONS_ARRAY")


with open(root_path + json_filename) as json_file:
    obj = json.load(json_file)

target_obj = json_util.go_to(obj, extract_path)

target_ss = json.dumps(target_obj)
ss = json.dumps(obj)
ss = ss.replace(target_ss, '""')
obj = json.loads(ss)

with open(root_path + json_filename, 'w') as json_file:
    json.dump(obj, json_file, indent=2)

with open(root_path + 'my_auto_save_legendary_dup_REGIONS.json', 'w') as json_file:
    json.dump(target_obj, json_file, indent=2)