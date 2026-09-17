from collections import defaultdict
from antoshka.totalwar.romeii.common import partition
from antoshka.totalwar.romeii.fixed.db import (list_faction_buildings as fixed_db__list_faction_buildings,
                                               list_faction_buildings_names as fixed_db__list_faction_buildings_names)
from antoshka.totalwar.romeii.fixed.model import db as fixed_db, BuildingSuperchain
from antoshka.totalwar.romeii.fixed.model.campaign_name import CampaignName, CAMPAIGN_NAME_TO_CODE, faction_code_campaign_name
from .parser_util import add_parser


def region_effects(_):
    start_pos = fixed_db.RegionStartPos.select().where(fixed_db.RegionStartPos.campaign_code_name == CAMPAIGN_NAME_TO_CODE[CampaignName.Grand])
    regions = [s_.region for s_ in start_pos]


    effects = fixed_db.RegionEffects.select().where(fixed_db.RegionEffects.region.in_(regions))
    effects_dict = defaultdict(list)
    for e_ in effects:
        effects_dict[e_.region.code_name].append(e_)
    display_names = {r_.code_name: r_.settlement_name
                     for r_ in fixed_db.Region.select().where(
                        fixed_db.Region.code_name.in_(list(effects_dict.keys())))}
    for region_code, effects in effects_dict.items():
        print(region_code, display_names[region_code])
        for e_ in effects:
            print(e_.effect_name, e_.scope, e_.value)


def faction_buildings(args):
    campaign = CampaignName(args.campaign)
    factions = fixed_db.Faction.select().where(fixed_db.Faction.screen_name == args.faction)
    factions = [f_ for f_ in factions if faction_code_campaign_name(f_.code_name) == campaign]
    if len(factions) > 1 or len(factions) == 0:
        raise RuntimeError()
    faction = factions[0]

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


def attach_fixed_parser(sps):
    p = sps.add_parser('fixed')
    sps = p.add_subparsers()

    add_parser(sps, 'region-effects', func=region_effects)

    p = add_parser(sps, 'faction-buildings', func=faction_buildings)
    p.add_argument('campaign', type=str, default='Grand')
    p.add_argument('faction', type=str)
