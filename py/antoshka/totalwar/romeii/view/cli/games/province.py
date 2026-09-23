from collections import defaultdict
from antoshka.totalwar.romeii.common.datetime import utc_now
from antoshka.totalwar.romeii.games.model import db as games_db
from antoshka.totalwar.romeii.games.db import list_control_plan_regions
from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from antoshka.totalwar.romeii.regionsopt.fixed import effect_map
from antoshka.totalwar.romeii.view.cli.parser_util import add_parser
from .util import get_selected_game


def add_region(args):
    game = get_selected_game()

    conditions = [fixed_db.RegionStartPos.campaign_code_name == game.campaign_code,
                  fixed_db.Region.settlement_name.startswith(args.region_name)]
    regions = list(fixed_db.Region.select()
                   .join(fixed_db.RegionStartPos)
                   .where(*conditions))
    if len(regions) == 0:
        print('Region not found')
    elif len(regions) > 1:
        print(f'Multiple regions found: {(rr.settlement_name for rr in regions)}')
    else:
        regions = regions[0]
        region_owner = games_db.RegionControlPlan.create(game=game,
                                                         ts=utc_now(),
                                                         region_code=regions.code_name)
        print(f'Game (id={game.id}) own region (code={region_owner.region_code})')


def attach_region_parser(sps):
    p = sps.add_parser('region')
    sps = p.add_subparsers()

    p = add_parser(sps, 'add', func=add_region)
    p.add_argument('region_name', type=str)


def list_provinces(args):
    game = get_selected_game()
    region_codes = list_control_plan_regions(game.id)

    regions = fixed_db.Region.select().where(fixed_db.Region.code_name.in_(region_codes))


    provinces = defaultdict(list)
    for ro in regions:
        provinces[ro.province.province_name].append(ro)

    if args.bonus:
        # TODO: think more about it.

        regions_start_pos = fixed_db.RegionStartPos.select().where(
            fixed_db.RegionStartPos.campaign_code_name == game.campaign_code,
            fixed_db.RegionStartPos.region.in_(regions))
        regions_start_pos = {r_.region.code_name: r_ for r_ in regions_start_pos}

        for po_name, rs in provinces.items():
            print(po_name, ':')
            for r_ in rs:
                start_pos = regions_start_pos[r_.code_name]
                s = r_.settlement_name
                if start_pos.province_capital:
                    s += '*'
                if start_pos.resource:
                    s += str(start_pos.resource)
                if start_pos.port:
                    s += 'Port'
                print(s)

                for e_ in r_.effects:
                    e_key = (e_.effect_name, e_.scope)
                    if e_key in effect_map.province_stats:
                        print('province:', effect_map.province_stats[e_key], e_.value)
                    if e_key in effect_map.province_negate_stats:
                        print('province:', effect_map.province_stats[e_key], -e_.value)
                    if e_key in effect_map.faction_stats:
                        print('factionwide:', effect_map.province_stats[e_key], e_.value)
    else:
        for po_name, rs in provinces.items():
            print(po_name, ':', [r_.settlement_name for r_ in rs])


def attach_province_parser(sps):
    p = sps.add_parser('province')
    sps = p.add_subparsers()

    p = add_parser(sps, 'list', func=list_provinces)
    # bonus
    # Region resource, port, capital should be marked with suffix *, special effects in province regions.
    # Province:
    #   Region: ResourceName, Port, special effects.
    p.add_argument('--bonus',  action='store_true')

    attach_region_parser(sps)