import copy
from util import read_yaml, filter_tree
from solver import Solver, WorkflowItem
from stats import Stats, STATS_NAMES_LIST
from solution import Solution
from buildings_tree import BuildingsTree
from initial_candidates import initial_candidates



def use_solver_1():
    path = "buildings/getae.yaml"
    buildings = read_yaml(path)

    bt = BuildingsTree(buildings)
    solver = Solver(bt)

    workflow = [WorkflowItem("pick_major"),
                WorkflowItem("pick_minors"),
                WorkflowItem("pick_ports"),
                WorkflowItem("pick_other_major"),
                WorkflowItem("prune", {"leave_count": 2000}),
                WorkflowItem("pick_other_minor", {"region_idx": 1}),
                WorkflowItem("prune", {"leave_count": 2000}),
                WorkflowItem("pick_other_minor", {"region_idx": 2}),
                WorkflowItem("prune", {"leave_count": 2000}),
                ]
    enough_food = lambda s: s.stats.food >= 0 and s.stats.order > 0
    good_food = lambda s: s.food >= 5 and s.order > 4
    more_wealth = lambda s_1, s_2: s_1 if s_1.wealth > s_2.wealth else s_2
    prune_heuristic = lambda s: (-min(s.stats.food, 0) + -min(s.stats.order, 0), -s.stats.wealth)

    solver.solve(3, [0, 2], [Solution(3)], workflow, enough_food, more_wealth, prune_heuristic)
    print(len(solver.candidates))
    print(solver.candidates[0])
    print(solver.candidates[-1])

    ss = list(filter(enough_food, solver.candidates))
    print(len(ss))

def test_filter_tree():
    path = "buildings/getae.yaml"
    buildings = read_yaml(path)

    filtered, other = filter_tree('Settlement', buildings)
    print(filtered)
    print(other)

def test_stats():
    path = "buildings/getae.yaml"
    buildings = read_yaml(path)
    bt = BuildingsTree(buildings)

    regions_str = "High King's Hold,Tribal Oppidum,Lynchet,Mead Hall,Cattle Ranch|Cattle Ranch,Sluiced Mine,Tribal Pagus"
    regions_str_list = regions_str.split('|')
    regions = list(map(lambda x: [] if not x else [s.strip() for s in x.split(',')], regions_str_list))

    def print_stats(stats):
        for stat_name in STATS_NAMES_LIST:
            print(stat_name, ":", getattr(stats, stat_name))

    s = Stats()
    for region in regions:
        for building_name in region:
            print(building_name)
            print_stats(bt.buildings_stats[building_name])
            s += bt.buildings_stats[building_name]
    print("Total")
    print_stats(s)
    print(s.wealth)

def test_deepcopy():
    s = copy.deepcopy(Solution(2))
    print(s, s.stats.food)


test_stats()