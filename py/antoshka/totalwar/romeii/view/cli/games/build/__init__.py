from .foundation import attach_foundation_parser
from .opt import attach_opt_parser
from .build import attach_build_commands


def attach_build_parser(sps):
    p = sps.add_parser('build')
    sps = p.add_subparsers()

    attach_build_commands(sps)
    attach_foundation_parser(sps)
    attach_opt_parser(sps)

    # foundation
    # list Province Name
    # gen Province Name

    # opt (no need to save it for now. Just be able to run would be enough.)
    # must provide foundation ID for that. Or can provide Province Name and will select latest foundation.
    # also must provide additional arguments.
