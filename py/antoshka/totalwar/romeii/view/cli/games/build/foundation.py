from collections import defaultdict
import pprint
from playhouse.shortcuts import model_to_dict
from antoshka.totalwar.romeii.common.datetime import utc_now
from antoshka.totalwar.romeii.games.model import db as games_db, ProvinceBuild, ProvinceBuildKind
from antoshka.totalwar.romeii.games.db import list_control_plan_regions
from antoshka.totalwar.romeii.fixed.model import db as fixed_db, BuildingSuperchain
from antoshka.totalwar.romeii.fixed.db import (list_faction_buildings as fixed_db__list_faction_buildings)
from antoshka.totalwar.romeii.view.cli.parser_util import add_parser
from antoshka.totalwar.romeii.view.cli.games.util import get_selected_game, approx_province_by_name
from .foundation_util import gen_foundation as gen_foundation_


def gen_foundation(args):
    foundation = gen_foundation_(args.province)
    pprint.pprint(model_to_dict(foundation))


def province_build_screen(pb: ProvinceBuild) -> ProvinceBuild:
    province_name = fixed_db.Province.get_by_id(pb.province_code).province_name
    named_regions_build = {}
    for  r_code, building_codes in pb.regions_build.items():
        r_name = fixed_db.Region.get_by_id(r_code).settlement_name
        bc_list = list(fixed_db.BuildingCulture.select()
                       .join(fixed_db.BuildingCultureScreen)
                       .where(fixed_db.BuildingCulture.building_code_name.in_(building_codes)))
        all_building_names = defaultdict(list)
        for bc in bc_list:
            all_building_names[bc.building_code_name].append(bc.screen.get().building_name)
        for _, names in all_building_names.items():
            if len(set(names)) > 1:
                raise RuntimeError()
        all_building_names = {code: names[0] for code, names in all_building_names.items()}

        building_names = [all_building_names[b_c] for b_c in building_codes]
        named_regions_build[r_name] = building_names
    return ProvinceBuild(province_name, named_regions_build)


def list_foundation(args):
    game = get_selected_game()
    foundations = games_db.ProvinceBuild.select().where(games_db.ProvinceBuild.game == game,
                                                        games_db.ProvinceBuild.status == ProvinceBuildKind.Foundation)
    if args.codes:
        for fo in foundations:
            pprint.pprint([f'id: {fo.id}', fo.build])
    else:
        for fo in foundations:
            pb = ProvinceBuild.from_serializable(fo.build)
            pb = province_build_screen(pb)
            pprint.pprint([f'id: {fo.id}', pb.to_serializable()])


def attach_foundation_parser(sps):
    p = sps.add_parser('foundation')
    sps = p.add_subparsers()

    p = add_parser(sps, 'gen', func=gen_foundation)
    p.add_argument('province', type=str)

    p = add_parser(sps, 'list', func=list_foundation)
    p.add_argument('--codes', action='store_true')