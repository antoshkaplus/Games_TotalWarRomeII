import typing as ty
from antoshka.totalwar.romeii.regionsopt.solver import Solver, WorkflowItem
from antoshka.totalwar.romeii.regionsopt.solution import Solution
from antoshka.totalwar.romeii.regionsopt.buildings_tree import BuildingsTree
from antoshka.totalwar.romeii.regionsopt.initial_candidates import initial_candidates
from antoshka.totalwar.romeii.regionsopt.building import Building
from .stats import Stats


type BuildingId = str
type Idx = int
type RegionBuild = ty.List[str]
type ProvinceBuild = ty.List[RegionBuild]


# To provide extra_stats
# we need to pick up primary build for every province and pick bonuses from those.
# no need for current builds. Only primary build matters.


class GameParams:
    def __init__(self, buildings: ty.Dict[BuildingId, Building], extra_stats: Stats):
        self.buildings = buildings
        self.extra_stats = extra_stats

class ProvinceParams:
    def __init__(self, regions: ProvinceBuild, port_regions: ty.List[Idx], no_major: bool):
        """
        :param regions: First region must be a major, otherwise `no_major` should be set to True.
        """
        self.regions = regions
        self.port_regions = port_regions
        self.no_major = no_major

class AlgoParams:
    def __init__(self, prune_sz: int = 2000):
        self.prune_sz = prune_sz

class SolutionParams:
    def __init__(self, min_food: int = 0, min_order: int = 0,
                 depth: ty.Optional[int] = None, no_resources: bool = False):
        self.min_food = min_food
        self.min_order = min_order
        self.depth = depth
        self.no_resources = no_resources


class ApplySolverParams:
    def __init__(self, game_params: GameParams, province_params: ProvinceParams,
                 solution_params: SolutionParams, algo_params: AlgoParams):
        self.game_params = game_params
        self.province_params = province_params
        self.solution_params = solution_params
        self.algo_params = algo_params


def apply_solver(params: ApplySolverParams) -> ty.Optional[Solution]:
    # fixed_db_path =  '/home/antoshkaplus/Documents/Games_TotalWarRomeII/data_lfs/fixed.db'
    # DB.init(fixed_db_path)
    # with DB:
    #     buildings = list_buildings('rom_getae')
    # buildings = {bb.name: bb for bb in buildings}

    bt = BuildingsTree(params.game_params.buildings,
                       params.solution_params.no_resources,
                       params.solution_params.depth)
    solver = Solver(bt)

    workflow = []
    if not params.province_params.no_major:
        workflow += [WorkflowItem("pick_major")]
    workflow += [
        WorkflowItem("pick_minors"),
        WorkflowItem("pick_ports")
    ]
    if not params.province_params.no_major:
        workflow += [WorkflowItem("pick_other_major")]

    workflow += [WorkflowItem("prune", {"leave_count": params.algo_params.prune_sz})]
    for i in range(1, len(params.province_params.regions)):
        workflow.append(WorkflowItem("pick_other_minor", {"region_idx": i}))
        workflow.append(WorkflowItem("prune", {"leave_count": params.algo_params.prune_sz}))

    min_food = params.solution_params.min_food
    min_order = params.solution_params.min_order
    prune_heuristic = lambda s: (-min(s.stats.food-min_food, 0) + -min(s.stats.order-min_order, 0), -s.stats.wealth)

    candidates = initial_candidates(params.province_params.regions, bt)
    # for c in candidates:
    #     if research:  # param research=False
    #         c.add(0, 'Bardic Circle', bt.buildings_stats['Bardic Circle'])

    solver.solve(len(params.province_params.regions), params.province_params.port_regions, candidates, workflow, prune_heuristic)
    candidates = solver.candidates
    candidates = list(filter(lambda x: x.stats.food >= min_food and x.stats.order >= min_order, candidates))
    print('Apply solver:', len(candidates), None if not candidates else candidates[0])

    if candidates:
        return candidates[0]
    return None
