

def subscriptable(obj):
    return hasattr(obj, '__getitem__')


def go_to(obj, path: str):
    """
    :param path:
    * /  - separator
    * [] - matches array of nodes
    * ABC - matches a node with `Name` ABC, goes under `Nodes` structure.
    """
    if not path:
        return obj

    if not subscriptable(obj) or isinstance(obj, str):
        return

    idx = path.find('/')
    if idx == -1:
        # expect a node with`Name` equal to path leftover
        if ('Name' not in obj) or (obj['Name'] != path):
            return
        return obj['Nodes']

    prefix = path[:idx]
    if prefix == '[]':
        res = [go_to(item, path[idx + 1:]) for item in obj]
        res = [r for r in res if r]
        if len(res) == 1:
            res = res[0]
        return res

    if ('Name' not in obj) or (obj['Name'] != prefix):
        return

    return go_to(obj['Nodes'], path[idx + 1:])


def go_to_list(obj, path: str) -> list:
    """
    :param path:
    * /  - separator
    * [] - matches array of nodes
    * ABC - matches a node with `Name` ABC, goes under `Nodes` structure.
    """
    if not path:
        return [obj]

    if not subscriptable(obj) or isinstance(obj, str):
        return []

    idx = path.find('/')
    if idx == -1:
        # expect a node with`Name` equal to path leftover
        if ('Name' not in obj) or (obj['Name'] != path):
            return []
        return obj['Nodes']

    prefix = path[:idx]
    if prefix == '[]':
        res = []
        for item in obj:
            res.extend(go_to_list(item, path[idx + 1:]))
        return res

    if ('Name' not in obj) or (obj['Name'] != prefix):
        return []

    return go_to_list(obj['Nodes'], path[idx + 1:])