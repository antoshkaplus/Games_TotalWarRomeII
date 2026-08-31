import yaml
import typing
import traceback


def read_yaml(path):
    with open(path, 'r') as fp:
        return yaml.full_load(fp)


def filter_tree(root_name, tree):
    tree = dict(tree)
    filtered = {root_name: tree[root_name]}
    del tree[root_name]
    prev_sz = 0
    while prev_sz != len(filtered):
        prev_sz = len(filtered)

        for item_name, item in list(tree.items()):
            try:
                if item['parent'] in filtered:
                    filtered[item_name] = item
                    del tree[item_name]
            except:
                print(item_name)
                traceback.print_exc()
                raise

    return filtered, tree


def filter_tree_many(root_names, tree, depth=None):
    tree = dict(tree)
    filtered = dict((root_name, tree[root_name]) for root_name in root_names)
    for root_name in root_names:
        del tree[root_name]

    cur_depth = 1
    new_filtered = filtered
    while new_filtered and (depth is None or depth > cur_depth):
        new_filtered = {}
        for item_name, item in list(tree.items()):
            try:
                if item['parent'] in filtered:
                    new_filtered[item_name] = item
                    del tree[item_name]
            except:
                print(item_name)
                traceback.print_exc()
                raise
        cur_depth += 1
        filtered.update(new_filtered)

    return filtered, tree


def leaf_names(tree) -> typing.List[str]:
    parents = set()
    for k, v in tree.items():
        parents.add(v['parent'])
    return [k for k in tree.keys() if k not in parents]