import copy
import itertools
import typing
from solution import Solution
from buildings_tree import BuildingsTree


class WorkflowItem:
    def __init__(self, func_name, kwargs={}):
        self.func_name = func_name
        self.kwargs = kwargs


class Solver:
    def __init__(self, buildings_tree : BuildingsTree):
        self.buildings_tree = buildings_tree

    def solve(self,
              regions_count     : int,
              port_regions      : typing.List[int],
              init_candidates   : typing.List[Solution],
              workflow          : typing.List[WorkflowItem],
              prune_heuristic):

        # port_regions : list of indices of ports
        # feasible: takes in solution, should decide if feasible or not
        # better: takes in two solution, returns a better one
        # prune_heuristic: provides key for sorting solutions, smaller -> better

        self.regions_count = regions_count
        self.port_regions = port_regions
        self.prune_heuristic = prune_heuristic

        self.candidates = list(init_candidates)

        for item in workflow:
            getattr(self, item.func_name)(**item.kwargs)

    def pick_major(self):
        # check if has one already:
        if self.candidates[0].regions[0] & self.buildings_tree.major_leafs_names:
            return

        new_candidates = []
        for c in self.candidates:
            for leaf_name in self.buildings_tree.major_leafs_names:
                nc = copy.deepcopy(c)
                nc.add(0, leaf_name, self.buildings_tree.buildings_stats[leaf_name])
                new_candidates.append(nc)
        self.candidates = new_candidates

    def pick_minors(self):
        minors_indices = []
        c = self.candidates[0]
        for i in range(1, self.regions_count):
            if not (c.regions[i] & self.buildings_tree.minor_leafs_names):
                minors_indices.append(i)

        new_candidates = []
        for c in self.candidates:
            for combination in itertools.combinations_with_replacement(self.buildings_tree.minor_leafs_names, len(minors_indices)):
                nc = copy.deepcopy(c)
                for i in range(len(minors_indices)):
                    nc.add(minors_indices[i], combination[i], self.buildings_tree.buildings_stats[combination[i]])
                new_candidates.append(nc)
        if new_candidates: self.candidates = new_candidates

    def pick_ports(self):
        if len(self.port_regions) == 0:
            return

        port_indices = []
        c = self.candidates[0]
        for i in self.port_regions:
            if not (c.regions[i] & self.buildings_tree.port_leafs_names):
                port_indices.append(i)

        new_candidates = []
        for c in self.candidates:
            for combination in itertools.combinations_with_replacement(self.buildings_tree.port_leafs_names, len(port_indices)):
                nc = copy.deepcopy(c)
                for i in range(len(port_indices)):
                    nc.add(port_indices[i], combination[i], self.buildings_tree.buildings_stats[combination[i]])
                new_candidates.append(nc)
        if new_candidates: self.candidates = new_candidates

    def pick_other_major(self):
        new_candidates = []
        for c in self.candidates:
            intersection = c.regions[0] & self.buildings_tree.other_major_leafs_names
            for combination in itertools.combinations(self.buildings_tree.other_major_leafs_names - intersection, 4 - len(intersection)):
                nc = copy.deepcopy(c)
                for comb_item in combination:
                    nc.add(0, comb_item, self.buildings_tree.buildings_stats[comb_item])
                new_candidates.append(nc)
        if new_candidates: self.candidates = new_candidates

    def pick_other_minor(self, region_idx : int):
        new_candidates = []
        for c in self.candidates:
            intersection = c.regions[region_idx] & self.buildings_tree.other_minor_leafs_names
            for combination in itertools.combinations(self.buildings_tree.other_minor_leafs_names, 2 - len(intersection)):
                nc = copy.deepcopy(c)
                for comb_item in combination:
                    nc.add(region_idx, comb_item, self.buildings_tree.buildings_stats[comb_item])
                new_candidates.append(nc)
        if new_candidates: self.candidates = new_candidates

    def prune(self, leave_count):
        self.candidates.sort(key=self.prune_heuristic)
        self.candidates = self.candidates[:leave_count]