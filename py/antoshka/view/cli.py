

def add_parser(sps, name, help=None, func=None):
    p = sps.add_parser(name, help=help)
    p.set_defaults(func=func)
    return p
