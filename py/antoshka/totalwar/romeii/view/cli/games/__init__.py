from .build import attach_build_parser
from .game import attach_game_parser
from .province import attach_province_parser


def attach_games_parser(sps):
    p = sps.add_parser('games')
    sps = p.add_subparsers()

    attach_game_parser(sps)
    attach_build_parser(sps)
    attach_province_parser(sps)



    # build province

    # province optimize - see regions, will know names, capital and cpecial effect.