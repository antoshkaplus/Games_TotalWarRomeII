
from faction_stats import faction_stats

STATS_NAMES_LIST = ['wealth_pct_all', 'wealth_pct_industry', 'wealth_pct_mnfr', 'wealth_pct_mining', 'wealth_pct_agri', 'wealth_pct_farming', 'wealth_pct_com',
                    'wealth_pct_culture', 'wealth_pct_fun',
                    'wealth_subsistence', 'wealth_fun', 'wealth_mnfr', 'wealth_mari_com', 'wealth_local_com',
                    'wealth_mining', 'wealth_learning', 'wealth_farming', 'wealth_livestock',
                    'order', 'food']


class Stats:
    def __init__(self, stats_dict={}):
        self.wealth_pct_all = 0
        self.wealth_pct_industry = 0
        self.wealth_pct_mnfr = 0
        self.wealth_pct_mining = 0
        self.wealth_pct_agri = 0
        self.wealth_pct_farming = 0
        self.wealth_pct_com = 0
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
        for stat_name in STATS_NAMES_LIST:
            setattr(self, stat_name, stats_dict.get(stat_name, 0))

    @property
    def wealth(self):
        w = (0.01 * self.wealth_subsistence * (100 + self.wealth_pct_all) +
             0.01 * self.wealth_fun * (100 + faction_stats.wealth_pct_culture + self.wealth_pct_all
                                       + self.wealth_pct_culture + self.wealth_pct_fun) +
             0.01 * self.wealth_learning * (100 + faction_stats.wealth_pct_culture + self.wealth_pct_all
                                            + self.wealth_pct_culture) +
             0.01 * self.wealth_mnfr * (100 + faction_stats.wealth_pct_industry + self.wealth_pct_all
                                        + self.wealth_pct_industry + self.wealth_pct_mnfr) +
             0.01 * self.wealth_mining * (100 + faction_stats.wealth_pct_industry + self.wealth_pct_all
                                          + self.wealth_pct_industry + self.wealth_pct_mining) +
             0.01 * (self.wealth_mari_com + self.wealth_local_com) * (100 + faction_stats.wealth_pct_com
                                                                      + self.wealth_pct_all + self.wealth_pct_com) +
             0.01 * self.wealth_farming * (100 + faction_stats.wealth_pct_agri
                                           + self.wealth_pct_all + self.wealth_pct_agri + self.wealth_pct_farming) +
             0.01 * self.wealth_livestock * (100 + faction_stats.wealth_pct_agri
                                             + self.wealth_pct_all + self.wealth_pct_agri))
        return w

    def __iadd__(self, other):
        for stat_name in STATS_NAMES_LIST:
            setattr(self, stat_name, getattr(self, stat_name) + getattr(other, stat_name))
        return self

    def __isub__(self, other):
        for stat_name in STATS_NAMES_LIST:
            setattr(self, stat_name, getattr(self, stat_name) - getattr(other, stat_name))
        return self
