import json
import argparse
import typing as ty
import pathlib
from antoshka.totalwar.romeii import json_util


ROOT_PATH = pathlib.Path('/home/antoshkaplus/Documents/Games_TotalWarRomeII/')


def json_extract_path(obj, extract_path: str) -> ty.Tuple[ty.Any, ty.Any]:
    target_obj = json_util.go_to(obj, extract_path)

    target_ss = json.dumps(target_obj)
    ss = json.dumps(obj)
    ss = ss.replace(target_ss, '""')
    obj = json.loads(ss)
    return target_obj, obj


parser = argparse.ArgumentParser(description='Extract Path CLI')
parser.add_argument('source_path', type=pathlib.Path, help='Source json file path')
parser.add_argument('--game-header', action='store_true')
parser.add_argument('--regions', action='store_true')
parser.add_argument('--setup', action='store_true')
parser.add_argument('--custom-path', action='store_true')
args = parser.parse_args()


source_json_path = args.source_path
if not source_json_path.relative_to(ROOT_PATH):
    source_json_path = ROOT_PATH / source_json_path

with open(source_json_path) as json_file:
    obj = json.load(json_file)


if args.game_header:
    extract_path = 'CAMPAIGN_SAVE_GAME/[]/SAVE_GAME_HEADER'
    target_obj, obj = json_extract_path(obj, extract_path)

    header_json_path = source_json_path.with_stem(source_json_path.stem + '-HEADER')
    with open(header_json_path, 'w') as json_file:
        json.dump(target_obj, json_file, indent=2)

    extract_path = 'CAMPAIGN_SAVE_GAME/[]/CAMPAIGN_SAVE_GAME/[]/SAVE_GAME_HEADER'
    target_obj, obj = json_extract_path(obj, extract_path)

    header_json_path = source_json_path.with_stem(source_json_path.stem + '-HEADER-2')
    with open(header_json_path, 'w') as json_file:
        json.dump(target_obj, json_file, indent=2)

if args.regions:
    extract_path = ("CAMPAIGN_SAVE_GAME/[]/CAMPAIGN_SAVE_GAME/[]/"
                    "CAMPAIGN_ENV/[]/CAMPAIGN_MODEL/[]/WORLD/[]/"
                    "REGION_MANAGER/[]/REGIONS_ARRAY")
    target_obj, obj = json_extract_path(obj, extract_path)
    regions_json_path = source_json_path.with_stem(source_json_path.stem + '-REGIONS')
    with open(regions_json_path, 'w') as json_file:
        json.dump(target_obj, json_file, indent=2)

if args.setup:
    extract_path = ("CAMPAIGN_SAVE_GAME/[]/CAMPAIGN_SAVE_GAME/[]/"
                    "CAMPAIGN_ENV/[]/CAMPAIGN_SETUP")
    target_obj, obj = json_extract_path(obj, extract_path)
    setup_json_path = source_json_path.with_stem(source_json_path.stem + '-SETUP')
    with open(setup_json_path, 'w') as json_file:
        json.dump(target_obj, json_file, indent=2)


with open(source_json_path, 'w') as json_file:
    json.dump(obj, json_file, indent=2)
