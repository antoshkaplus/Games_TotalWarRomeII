import traceback
from stats import Stats


class Solution:
    def __init__(self, regions_count):
        self.regions = [set() for i in range(regions_count)]
        self.stats = Stats()

    def __repr__(self):
        try:
            return f"order: {self.stats.order}, food: {self.stats.food}, wealth: {self.stats.wealth}, {self.regions}"
        except:
            print(self.regions)
            traceback.print_exc()
            raise

    def add(self, region_idx, building_name, building_stats):
        try:
            self.regions[region_idx].add(building_name)
            self.stats += building_stats
        except:
            print(building_name, building_stats)
            raise

    def remove(self, region_idx, building_name, building_stats):
        self.regions[region_idx].remove(building_name)
        self.stats -= building_stats