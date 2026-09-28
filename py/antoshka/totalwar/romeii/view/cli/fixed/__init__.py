from antoshka.totalwar.romeii.view.cli.parser_util import add_parser
from .fixed import region_effects
from .faction import attach_faction_parser
from .building import attach_building_parser


def attach_fixed_parser(sps):
    p = sps.add_parser('fixed')
    sps = p.add_subparsers()

    attach_faction_parser(sps)
    attach_building_parser(sps)
    add_parser(sps, 'region-effects', func=region_effects)

