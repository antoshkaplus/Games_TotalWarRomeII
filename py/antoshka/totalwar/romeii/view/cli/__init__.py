from .games import attach_games_parser
from .fixed import attach_fixed_parser


def attach_cli_parsers(sps):
    attach_games_parser(sps)
    attach_fixed_parser(sps)
