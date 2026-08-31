import copy
import typing

from solution import Solution
from buildings_tree import BuildingsTree


def initial_candidates(regions_lists : typing.List[typing.List[str]], bt : BuildingsTree):
    # returns solution candidates

    candidates = [regions_lists]
    for r_i, r in enumerate(regions_lists):
        for b_i, b_name in enumerate(r):
            if b_name in bt.leafs:
                continue
            leafs = bt.find_leafs(b_name)
            new_candidates = []
            for leaf in leafs:
                if leaf not in r:
                    for c in candidates:
                        if leaf in c[r_i]:
                            continue
                        new_c = copy.deepcopy(c)
                        new_c[r_i][b_i] = leaf
                        new_candidates.append(new_c)
            if not new_candidates:
                raise RuntimeError(f"Unable to find leaf for {r}, {b_name}")
            candidates = new_candidates

    def list_to_solution(regions):
        solution = Solution(len(regions))
        for i, r in enumerate(regions):
            for name in r:
                solution.add(i, name, bt.buildings_stats[name])
        return solution

    candidates = list(map(list_to_solution, candidates))
    return candidates