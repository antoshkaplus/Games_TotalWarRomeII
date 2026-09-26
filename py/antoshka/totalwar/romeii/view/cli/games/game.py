from antoshka.totalwar.romeii.common.datetime import utc_now, date_to_str
from antoshka.totalwar.romeii.games.model import db as games_db
from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from antoshka.totalwar.romeii.fixed.model.campaign_name import CampaignName, CAMPAIGN_NAME_TO_CODE
from antoshka.totalwar.romeii.view.cli.fixed.faction import faction_by_name
from antoshka.totalwar.romeii.view.cli.parser_util import add_parser


def create_game_manually(args):
    campaign_name = CampaignName(args.campaign)
    faction = faction_by_name(args.faction, campaign_name)

    political_party = set(e_.political_party for e_ in faction.effects if e_.political_party)
    print(political_party)
    if len(political_party) == 1:
        political_party, = political_party
    else:
        if args.party not in political_party:
            raise RuntimeError()
        political_party = args.party

    now = utc_now()
    game = games_db.Game.create(campaign_code=CAMPAIGN_NAME_TO_CODE[campaign_name],
                                faction_code=faction.code_name,
                                political_party=political_party,
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
    p.add_argument('--party', type=str)

    # add_parser(sps, 'from-save')


def list_games(args):
    games = list(games_db.Game.select())
    games.sort(key=lambda x: x.last_selected, reverse=True)
    print(f'Count: {len(games)}')
    for g_ in games:
        s = f'id: {g_.id}, {g_.campaign_code} {g_.faction_code} {g_.political_party}, created: {date_to_str(g_.create_ts)}'
        print(s)


def attach_game_parser(sps):
    p = sps.add_parser('game')
    sps = p.add_subparsers()

    attach_create_game_parser(sps)
    add_parser(sps, 'list', func=list_games)

    # need list command
