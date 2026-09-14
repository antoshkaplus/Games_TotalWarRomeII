import typing as ty
from collections import defaultdict
from antoshka.totalwar.romeii.common.datetime import utc_now
from antoshka.totalwar.romeii.games.model import db as games_db
from antoshka.totalwar.romeii.games.db import list_control_plan_regions
from antoshka.totalwar.romeii.campaign_name import CampaignName, CAMPAIGN_NAME_CODE
from .parser_util import add_parser
from antoshka.totalwar.romeii.fixed.model import db as fixed_db


def get_selected_game():
    return games_db.Game.select().order_by(games_db.Game.last_selected.desc()).first()


def create_game_manually(args):
    campaign_name = CampaignName(args.campaign)
    faction = fixed_db.Faction.select().where(fixed_db.Faction.screen_name == args.faction).get()
    now = utc_now()

    game = games_db.Game.create(campaign_code=CAMPAIGN_NAME_CODE[campaign_name],
                                faction_code=faction.code_name,
                                create_ts=now,
                                last_selected=now)

    print('Created new game:',
          game.id, game.campaign_code, game.faction_code,
          game.create_ts, game.last_selected)


def attach_create_game_parser(sps):
    p = sps.add_parser('create')
    sps = p.add_subparsers()

    p = add_parser(sps, 'manually', func=create_game_manually)
    p.add_argument('campaign', type=str)
    p.add_argument('faction', type=str)

    # add_parser(sps, 'from-save')


def add_region(args):
    game = get_selected_game()

    conditions = [fixed_db.RegionStartPos.campaign_code_name == game.campaign_code,
                  fixed_db.Region.settlement_name.startswith(args.region)]
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
    p.add_argument('region', type=str)


def list_provinces(_):
    game = get_selected_game()
    region_codes = list_control_plan_regions(game.id)

    regions = fixed_db.Region.select().where(fixed_db.Region.code_name.in_(region_codes))
    regions_start_pos = fixed_db.RegionStartPos.select().where(
        fixed_db.RegionStartPos.campaign_code_name == game.campaign_code,
        fixed_db.RegionStartPos.region.in_(regions))

    provinces = defaultdict(list)
    for ro in regions:
        provinces[ro.province.province_name].append(ro.settlement_name)
    for po_name, ro_names in provinces.items():
        print(po_name, ':', ro_names)


def optimize_province(args):
    # TODO: figure out foundation.
    game = get_selected_game()

    owned_regions = list_control_plan_regions(game.id)
    province = fixed_db.Province.select().where(fixed_db.Province.province_name == args.province).get_or_none()
    if not province:
        raise RuntimeError()

    regions = [ro for ro in province.regions if ro.code_name in owned_regions]
    regions: ty.List[fixed_db.Region]

    # need to figure out which one is Capital, resources and Capital region.



def attach_games_parser(sps):
    p = sps.add_parser('games')
    sps = p.add_subparsers()

    attach_create_game_parser(sps)
    attach_region_parser(sps)

    add_parser(sps, 'list-provinces', func=list_provinces)
    p = add_parser(sps, 'opt-province', func=optimize_province)
    p.add_argument('province')

    # build province

    # province optimize - see regions, will know names, capital and cpecial effect.