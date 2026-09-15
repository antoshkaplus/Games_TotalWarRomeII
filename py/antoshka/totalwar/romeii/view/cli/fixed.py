from collections import defaultdict
from antoshka.totalwar.romeii.campaign_name import CampaignName, CAMPAIGN_NAME_TO_CODE
from antoshka.totalwar.romeii.fixed.model import db as fixed_db
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


def attach_fixed_parser(sps):
    p = sps.add_parser('fixed')
    sps = p.add_subparsers()

    add_parser(sps, 'region-effects', func=region_effects)