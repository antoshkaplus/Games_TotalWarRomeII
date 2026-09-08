import typing as ty
import copy
import collections
from util import leaf_names, filter_tree, filter_tree_many
from stats import Stats
from .building import Building, Name


class BuildingsTree:
    def __init__(self, buildings_dict: ty.Dict[Name, Building], no_resources=False, depth=None):
        """
        :param buildings_dict: buildings by name.
        :param depth: synonymous to `pack` file building `level` but start counting from 1 instead of 0.
        """
        root_names = [k for k, v in buildings_dict.items() if v.parent_name is None]
        buildings_dict, _ = filter_tree_many(root_names, buildings_dict, depth)

        # need_resource nodes are leafs so we can just remove them
        if no_resources:
            self._buildings_dict = dict((k, copy.deepcopy(v)) for k, v in buildings_dict.items() if not v.need_resource)
        else:
            self._buildings_dict = copy.deepcopy(buildings_dict)

        self._leafs_list = leaf_names(self._buildings_dict)
        self._building_leafs = collections.defaultdict(set)
        self.__fill_building_leaf()

        self.buildings_stats = {}
        for k, v in self._buildings_dict.items():
            v.name = k
            self.buildings_stats[k] = Stats(v)

        resource, other = {}, {}
        for k, v in self._buildings_dict.items():
            if v.get('resource', False):
                resource[k] = v
            else:
                other[k] = v
        self.resource_leafs_names = set(leaf_names(resource))


        major_prime, minor_prime = {}, {}
        major_other, minor_other = {}, {}
        port = {}
        for name, building in self._buildings_dict.items():
            if building.primary:
                if building.major:
                    major_prime[name] = building
                else:
                    minor_prime[name] = building
            elif building.secondary_port:
                port[name] = building
            else: # secondary
                if building.major:
                    major_other[name] = building
                if building.minor:
                    minor_other[name] = building

        self.major_leafs_names = set(leaf_names(major_prime))
        self.minor_leafs_names = set(leaf_names(minor_prime))
        self.port_leafs_names = set(leaf_names(port))
        self.other_major_leafs_names = set(leaf_names(major_other))
        self.other_minor_leafs_names = set(leaf_names(minor_other))

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
                parent = self._buildings_dict[name].parent_name
                if parent:
                    for leaf_name in self._building_leafs[name]:
                        self._building_leafs[parent].add(leaf_name)
                    new_names.append(parent)
            found_names = new_names