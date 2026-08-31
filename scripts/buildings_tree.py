import copy
import collections

from util import leaf_names, filter_tree, filter_tree_many
from stats import Stats


class BuildingsTree:
    def __init__(self, buildings_dict, no_resources=False, depth=None):
        root_names = [k for k, v in buildings_dict.items() if v['parent'] is None]
        buildings_dict, _ = filter_tree_many(root_names, buildings_dict, depth)

        # need_resource nodes are leafs so we can just remove them
        if no_resources:
            self._buildings_dict = dict((k, copy.deepcopy(v)) for k, v in buildings_dict.items() if 'need_resource' not in v)
        else:
            self._buildings_dict = copy.deepcopy(buildings_dict)

        self._leafs_list = leaf_names(self._buildings_dict)
        self._building_leafs = collections.defaultdict(set)
        self.__fill_building_leaf()

        self.buildings_stats = {}
        for k, v in self._buildings_dict.items():
            v['name'] = k
            self.buildings_stats[k] = Stats(v)

        resource, other = {}, {}
        for k, v in self._buildings_dict.items():
            if v.get('resource', False):
                resource[k] = v
            else:
                other[k] = v
        self.resource_leafs_names = set(leaf_names(resource))

        major, other = filter_tree('Settlement', other)
        self.major_leafs_names = set(leaf_names(major))
        minor, other = filter_tree('Farmstead', other)
        self.minor_leafs_names = set(leaf_names(minor))
        port, other = filter_tree('Port', other)
        self.port_leafs_names = set(leaf_names(port))

        self.other_major_leafs_names = self.compute_other_major_leafs(other)
        self.other_minor_leafs_names = self.compute_other_minor_leafs(other)


    @property
    def leafs(self):
        return self._leafs_list

    def find_leafs(self, building_name) -> set:
        return self._building_leafs[building_name]

    def __fill_building_leaf(self):
        for leaf in self.leafs:
            self._building_leafs[leaf].add(leaf)
        found_names = list(self.leafs)
        while found_names:
            new_names = []
            for name in found_names:
                parent = self._buildings_dict[name]['parent']
                if parent:
                    for leaf_name in self._building_leafs[name]:
                        self._building_leafs[parent].add(leaf_name)
                    new_names.append(parent)
            found_names = new_names

    def compute_other_minor_leafs(self, other):
        # other is without major, minor main buildings, without port
        _, minor = filter_tree('Commons', other)
        _, minor = filter_tree('Warrior Lodge', minor)
        return set(leaf_names(minor))

    def compute_other_major_leafs(self, other):
        # other is without major, minor main buildings, without port
        _, major = filter_tree('Well', other)
        _, major = filter_tree('Pit Mine', major)
        return set(leaf_names(major))