import copy

from util import read_yaml, filter_tree
from solver import Solver, WorkflowItem
from solution import Solution
from buildings_tree import BuildingsTree
from initial_candidates import initial_candidates

import argparse


def use_solver(regions, port_regions, min_food, min_order, no_resources=False, no_major=False, prune_sz=2000, research=False, depth=None):

    path = "buildings/getae.yaml"
    buildings = read_yaml(path)

    bt = BuildingsTree(buildings, no_resources, depth)
    solver = Solver(bt)

    workflow = []
    if not no_major:
        workflow += [WorkflowItem("pick_major")]
    workflow += [
        WorkflowItem("pick_minors"),
        WorkflowItem("pick_ports")
    ]
    if not no_major:
        workflow += [WorkflowItem("pick_other_major")]

    workflow += [WorkflowItem("prune", {"leave_count": prune_sz})]
    for i in range(1, len(regions)):
        workflow.append(WorkflowItem("pick_other_minor", {"region_idx": i}))
        workflow.append(WorkflowItem("prune", {"leave_count": prune_sz}))

    prune_heuristic = lambda s: (-min(s.stats.food-min_food, 0) + -min(s.stats.order-min_order, 0), -s.stats.wealth)

    candidates = initial_candidates(regions, bt)
    for c in candidates:
        if research:
            c.add(0, 'Bardic Circle', bt.buildings_stats['Bardic Circle'])

    solver.solve(len(regions), port_regions, candidates, workflow, prune_heuristic)
    candidates = solver.candidates
    candidates = list(filter(lambda x: x.stats.food >= min_food and x.stats.order >= min_order, candidates))
    print(len(candidates), None if not candidates else candidates[0])


parser = argparse.ArgumentParser()
parser.add_argument('regions', type=str, help="r1b1,r1b2,..|r2b1,r2b2,...|..., province with existing buildings, must include Port if is there")
# don't need port regions, just add Port to regions argument
# parser.add_argument('--port-regions', type=str)
parser.add_argument('min_food', type=int)
parser.add_argument('min_order', type=int)
parser.add_argument('--prune-sz', type=int, default=2000)
parser.add_argument('--no-resources', action='store_true')
parser.add_argument('--no-major', action='store_true')
parser.add_argument('--research', action='store_true')
parser.add_argument('--depth', type=int, default=None)

args = parser.parse_args()
print(args)

regions_str = args.regions
regions_str_list = regions_str.split('|')
regions = list(map(lambda x: [] if not x else [s.strip() for s in x.split(',')], regions_str_list))

use_solver(regions, [], args.min_food, args.min_order, args.no_resources, args.no_major, args.prune_sz, args.research, args.depth)