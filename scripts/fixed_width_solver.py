import copy
import itertools
import types

from util import filter_tree, leaf_names
from solution import Solution


class FixedWidthSolver:
    def __init__(self, buildings):
        self.buildings = copy.deepcopy(buildings)
        for k, v in self.buildings.items():
            v['name'] = k

        major, other = filter_tree('Settlement', self.buildings)
        self.major_leafs_names = leaf_names(major)
        minor, other = filter_tree('Farmstead', other)
        self.minor_leafs_names = leaf_names(minor)
        port, other = filter_tree('Port', other)
        self.port_leafs_names = leaf_names(port)
        self.other_leafs_names = leaf_names(other)


    def solve(self, port_regions, feasible, better, heuristic, width):
        # feasible: takes in solution, should decide if feasible or not
        # better: takes in two solution, returns a better one

        self.port_regions = port_regions
        self.port_regions_count = port_regions.count(True)
        self.feasible = feasible
        self.better = better
        self.heuristic = heuristic
        self.width = width

        self.best_sol = None
        self.pick_major(Solution(self.port_regions))
        return self.best_sol


    def add_to_region(self, sol, region, name):
        sol[region].append(self.buildings[name])

    def add_many_to_region(self, sol, region, names):
        sol[region].extend([self.buildings[name] for name in names])

    def pop_from_region(self, sol, region):
        sol[region].pop()

    def pop_many_from_region(self, sol, region, count):
        sol[region] = sol[region][:-count]

    def update_best_sol(self, new_best):
        if self.best_sol is None:
            self.best_sol = copy.deepcopy(new_best)
            return True
        elif new_best is not None:
            best = self.better(self.best_sol, new_best)
            if best != self.best_sol:
                self.best_sol = copy.deepcopy(new_best)
                return True
        return False

    def pick_major(self, sol : Solution):
        for leaf_name in self.major_leafs_names:
            self.add_to_region(sol, 0, leaf_name)
            self.pick_other_major(sol)
            # check if best solution, should save if best
            self.pop_from_region(sol, 0)


    def pick_port_major(self, sol: Solution):
        if not self.port_regions[0]:
            self.pick_other_major(sol)
        else:
            for name in self.port_leafs_names:
                self.add_to_region(sol, 0, name)
                self.pick_other_major(sol)
                self.pop_from_region(sol, 0)

    def pick_other_major(self, sol : Solution):
        for combination in itertools.combinations(self.other_leafs_names, 4):
            self.add_many_to_region(sol, 0, combination)
            self.pick_minor(sol, 1)
            self.pop_many_from_region(sol, 0, len(combination))

    def pick_minor(self, sol : Solution, region_idx):
        if region_idx == sol.regions_count:
            if self.feasible(sol) and self.update_best_sol(sol):
                print(sol)
            return

        for name in self.minor_leafs_names:
            self.add_to_region(sol, region_idx, name)
            self.pick_other_minor(sol, region_idx)
            self.pop_from_region(sol, region_idx)

    def pick_port_minor(self, sol: Solution, region_idx):
        if not self.port_regions[region_idx]:
            self.pick_other_minor(sol, region_idx)
        else:
            for name in self.port_leafs_names:
                self.add_to_region(sol, region_idx, name)
                self.pick_other_minor(sol, region_idx)
                self.pop_from_region(sol, region_idx)

    def pick_other_minor(self, sol : Solution, minor_region_idx : int):
        # here first loop we add, but also putting result into a heap with value (heuristic_value, combination)
        result = []
        for combination in itertools.combinations(self.other_leafs_names, 2):
            self.add_many_to_region(sol, minor_region_idx, combination)
            result.append(types.SimpleNamespace(h=self.heuristic(sol), c=combination))
            self.pop_many_from_region(sol, minor_region_idx, len(combination))
        result.sort(key=lambda x: x.h)
        result = result[:self.width]
        for _, c in result:
            self.add_many_to_region(sol, minor_region_idx, c)
            self.pick_minor(sol, minor_region_idx + 1)
            self.pop_many_from_region(sol, minor_region_idx)

    # have to rework a lot actually.
    # it probably has to be almost full fledged iterative solution
    # I kind of have to add up on top of existing solution
