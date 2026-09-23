from collections import defaultdict
from antoshka.totalwar.romeii.common import partition
from antoshka.totalwar.romeii.fixed.db import (list_faction_buildings_names as fixed_db__list_faction_buildings_names)
from antoshka.totalwar.romeii.fixed.model import db as fixed_db, BuildingSuperchain
from antoshka.totalwar.romeii.fixed.model.campaign_name import CampaignName, faction_code_campaign_name
from antoshka.totalwar.romeii.view.cli.parser_util import add_parser



def faction_by_name(faction_name: str, campaign: CampaignName) -> fixed_db.Faction:
    factions = fixed_db.Faction.select().where(fixed_db.Faction.screen_name == faction_name)
    factions = [f_ for f_ in factions if faction_code_campaign_name(f_.code_name) == campaign]
    if len(factions) > 1 or len(factions) == 0:
        raise RuntimeError()
    return factions[0]


def faction_buildings(args):
    campaign = CampaignName(args.campaign)
    faction = faction_by_name(args.faction, campaign)

    buildings_names = fixed_db__list_faction_buildings_names(faction.code_name, campaign)

    buildings = list(fixed_db.Building.select().where(fixed_db.Building.code_name.in_(list(buildings_names))))
    resource_buildings, other_buildings = partition(lambda x: BuildingSuperchain(x.superchain).resource_kind, buildings)
    resource_codes = [b_.code_name for b_ in resource_buildings]
    by_superchain = defaultdict(list)
    for b_ in other_buildings:
        chain = BuildingSuperchain(b_.superchain)
        by_superchain[chain].append(b_.code_name)

    print('Resource')
    print({r_: buildings_names[r_] for r_ in resource_codes})
    for chain, codes in by_superchain.items():
        print(chain)
        print({r_: buildings_names[r_] for r_ in codes})


def faction_stats(args):
    campaign = CampaignName(args.campaign)
    faction = faction_by_name(args.faction, campaign)

    for e_ in faction.effects:
        e_: fixed_db.FactionEffect
        print(e_.political_party, e_.effect_bundle, e_.effect_name, e_.scope, e_.value)


def attach_faction_parser(sps):
    p = sps.add_parser('faction')
    sps = p.add_subparsers()

    p = add_parser(sps, 'buildings', func=faction_buildings)
    p.add_argument('campaign', type=str, default='Grand')
    p.add_argument('faction', type=str)

    p = add_parser(sps, 'stats', func=faction_stats)
    p.add_argument('campaign', type=str, default='Grand')
    p.add_argument('faction', type=str)