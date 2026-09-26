from antoshka.totalwar.romeii.common.serializable import Serializable


STATS_NAMES_LIST = ['wealth_pct_all', 'wealth_pct_industry', 'wealth_pct_mnfr', 'wealth_pct_mining',
                    'wealth_pct_agri', 'wealth_pct_farming', 'wealth_pct_com', 'wealth_pct_mari_com',
                    'wealth_pct_culture', 'wealth_pct_fun',
                    'wealth_subsistence', 'wealth_fun', 'wealth_mnfr', 'wealth_mari_com', 'wealth_local_com',
                    'wealth_mining', 'wealth_learning', 'wealth_farming', 'wealth_livestock',
                    'order', 'food',
                    'research_pct', 'research_pct_civil', 'research_pct_military',
                    'order_pct_foreign_culture']


class Stats(Serializable):
    def __init__(self, stats_dict={}):
        self.wealth_pct_all = 0
        self.wealth_pct_industry = 0
        self.wealth_pct_mnfr = 0
        self.wealth_pct_mining = 0
        self.wealth_pct_agri = 0
        self.wealth_pct_farming = 0
        self.wealth_pct_com = 0
        self.wealth_pct_mari_com = 0
        self.wealth_pct_culture = 0
        self.wealth_pct_fun = 0
        self.wealth_subsistence = 0
        self.wealth_fun = 0
        self.wealth_mnfr = 0
        self.wealth_mari_com = 0
        self.wealth_local_com = 0
        self.wealth_mining = 0
        self.wealth_learning = 0
        self.wealth_farming = 0
        self.wealth_livestock = 0
        self.order = 0
        self.food = 0

        self.research_pct = 0
        self.research_pct_civil = 0
        self.research_pct_military = 0

        self.order_pct_foreign_culture = 0
        for stat_name in STATS_NAMES_LIST:
            setattr(self, stat_name, stats_dict.get(stat_name, 0))

    @property
    def wealth(self):
        w = (0.01 * self.wealth_subsistence * (100 + self.wealth_pct_all) +
             0.01 * self.wealth_fun * (100 + self.wealth_pct_all + self.wealth_pct_culture + self.wealth_pct_fun) +
             0.01 * self.wealth_learning * (100 + self.wealth_pct_all + self.wealth_pct_culture) +
             0.01 * self.wealth_mnfr * (100 + self.wealth_pct_all + self.wealth_pct_industry + self.wealth_pct_mnfr) +
             0.01 * self.wealth_mining * (100 + self.wealth_pct_all + self.wealth_pct_industry + self.wealth_pct_mining) +
             0.01 * self.wealth_mari_com * (100 + self.wealth_pct_all + self.wealth_pct_com + self.wealth_pct_mari_com) +
             0.01 * self.wealth_local_com * (100 + self.wealth_pct_all + self.wealth_pct_com) +
             0.01 * self.wealth_farming * (100 + self.wealth_pct_all + self.wealth_pct_agri + self.wealth_pct_farming) +
             0.01 * self.wealth_livestock * (100 + self.wealth_pct_all + self.wealth_pct_agri))
        return w

    def __iadd__(self, other):
        for stat_name in STATS_NAMES_LIST:
            setattr(self, stat_name, getattr(self, stat_name) + getattr(other, stat_name))
        return self

    def __add__(self, other):
        res = Stats()
        for stat_name in STATS_NAMES_LIST:
            setattr(res, stat_name, getattr(self, stat_name) + getattr(other, stat_name))
        return res

    def __isub__(self, other):
        for stat_name in STATS_NAMES_LIST:
            setattr(self, stat_name, getattr(self, stat_name) - getattr(other, stat_name))
        return self

    @property
    def empty(self):
        for stat_name in STATS_NAMES_LIST:
            if getattr(self, stat_name) != 0.:
                return False
        return True

    def to_serializable(self):
        obj = {}
        for stat_name in STATS_NAMES_LIST:
            if getattr(self, stat_name) != 0.:
                obj[stat_name] = getattr(self, stat_name)
        return obj

    @staticmethod
    def from_serializable(obj) -> Stats:
        stats = Stats()
        for stat_name, stat_value in obj.items():
            setattr(stats, stat_name, stat_value)