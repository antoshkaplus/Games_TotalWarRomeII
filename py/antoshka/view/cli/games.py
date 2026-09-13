import peewee
from antoshka.totalwar.romeii.common.datetime import utc_now
from antoshka.totalwar.romeii.games.model import db as game_db
from antoshka.totalwar.romeii.campaign_name import CampaignName, CAMPAIGN_NAME_CODE
from .parser_util import add_parser
from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from ...totalwar.romeii.games.model.db import region_owner


def create_game_manually(args):
    campaign_name = CampaignName(args.campaign_name)
    faction = fixed_db.Faction.select().where(fixed_db.Faction.screen_name == args.faction).get()
    now = utc_now()

    game = game_db.Game.create(campaign_code=CAMPAIGN_NAME_CODE[campaign_name],
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
    game = game_db.Game.select().where(
        game_db.Game.last_selected == peewee.fn.MAX(game_db.Game.last_selected)).get()

    regions = list(fixed_db.Region.select().where(fixed_db.Region.settlement_name.startswith(args.region)))
    if len(regions) == 0:
        print('Region not found')
    elif len(regions) > 1:
        print(f'Multiple regions found: {(rr.settlement_name for rr in regions)}')
    else:
        regions = regions[0]
        region_owner = game_db.RegionOwner.create(game=game,
                                                  ts=utc_now(),
                                                  region_code=regions.code_name,
                                                  owner=True)
        print(f'Game (id={game.id}) own region (code={region_owner.region_code})')


def attach_region_parser(sps):
    p = sps.add_parser('region')
    sps = p.add_subparsers()

    p = add_parser(sps, 'add', func=add_region)
    p.add_argument('region', type=str)


def attach_games_parser(sps):
    p = sps.add_parser('games')
    sps = p.add_subparsers()

    attach_create_game_parser(sps)
    attach_region_parser(sps)

    # list provinces
    # build province
    # province optimize - see regions, will know names, capital and cpecial effect.