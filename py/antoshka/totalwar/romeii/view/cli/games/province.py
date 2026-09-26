from collections import defaultdict
from antoshka.totalwar.romeii.common.datetime import utc_now
from antoshka.totalwar.romeii.games.model import db as games_db
from antoshka.totalwar.romeii.games.db import list_control_plan_regions
from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from antoshka.totalwar.romeii.regionsopt.fixed import effect_map
from antoshka.totalwar.romeii.view.cli.parser_util import add_parser
from .util import get_selected_game, approx_province_by_name


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

    regions = list(fixed_db.Region.select().where(fixed_db.Region.code_name.in_(region_codes)))
    if len(regions) == 0:
        print('No regions in control plan.')

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


def add_province(args):
    game = get_selected_game()

    province = approx_province_by_name(args.province_name_prefix)
    now = utc_now()
    add_control_regions = [{'game': game.id,
                            'region_code': r_.code_name,
                            'ts': now}  for r_ in province.regions]
    games_db.RegionControlPlan.insert_many(add_control_regions).on_conflict_ignore().execute()
    print(f'Province `{province.province_name}` regions {', '.join(r_.settlement_name for r_ in province.regions)} in Control Plan.')


def attach_province_parser(sps):
    p = sps.add_parser('province')
    sps = p.add_subparsers()

    add_parser(sps, 'list', func=list_provinces)

    p = add_parser(sps, 'add', func=add_province)
    p.add_argument('province_name_prefix', type=str)

    # bonus
    # Region resource, port, capital should be marked with suffix *, special effects in province regions.
    # Province:
    #   Region: ResourceName, Port, special effects.
    p.add_argument('--bonus',  action='store_true')

    attach_region_parser(sps)