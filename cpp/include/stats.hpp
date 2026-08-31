#pragma once

struct Stats {
    // counted 20 fields
    int wealth_pct_all = 0;
    int wealth_pct_industry = 0;
    int wealth_pct_mnfr = 0;
    int wealth_pct_mining = 0;
    int wealth_pct_agri = 0;
    int wealth_pct_farming = 0;
    int wealth_pct_com = 0;
    int wealth_pct_culture = 0;
    int wealth_pct_fun = 0;
    int wealth_subsistence = 0;
    int wealth_fun = 0;
    int wealth_mnfr = 0;
    int wealth_mari_com = 0;
    int wealth_local_com = 0;
    int wealth_mining = 0;
    int wealth_learning = 0;
    int wealth_farming = 0;
    int wealth_livestock = 0;
    int order = 0;
    int food = 0;

    double wealth() const {
        double w = (0.01 * wealth_subsistence * (100 + wealth_pct_all) +
                    0.01 * wealth_fun * (100 + wealth_pct_all
                                         + wealth_pct_culture + wealth_pct_fun) +
                    0.01 * wealth_learning * (100 + wealth_pct_all
                                              + wealth_pct_culture) +
                    0.01 * wealth_mnfr * (100 + wealth_pct_all
                                          + wealth_pct_industry + wealth_pct_mnfr) +
                    0.01 * wealth_mining * (100 + wealth_pct_all
                                            + wealth_pct_industry + wealth_pct_mining) +
                    0.01 * (wealth_mari_com + wealth_local_com) * (100 + wealth_pct_all + wealth_pct_com) +
                    0.01 * wealth_farming * (100 + wealth_pct_all + wealth_pct_agri + wealth_pct_farming) +
                    0.01 * wealth_livestock * (100 + wealth_pct_all + wealth_pct_agri));
        return w;
    }

    Stats& operator+=(const Stats& other) {
        // counted 20 fields
        wealth_pct_all += other.wealth_pct_all;
        wealth_pct_industry += other.wealth_pct_industry;
        wealth_pct_mnfr += other.wealth_pct_mnfr;
        wealth_pct_mining += other.wealth_pct_mining;
        wealth_pct_agri += other.wealth_pct_agri;
        wealth_pct_farming += other.wealth_pct_farming;
        wealth_pct_com += other.wealth_pct_com;
        wealth_pct_culture += other.wealth_pct_culture;
        wealth_pct_fun += other.wealth_pct_fun;
        wealth_subsistence += other.wealth_subsistence;
        wealth_fun += other.wealth_fun;
        wealth_mnfr += other.wealth_mnfr;
        wealth_mari_com += other.wealth_mari_com;
        wealth_local_com += other.wealth_local_com;
        wealth_mining += other.wealth_mining;
        wealth_learning += other.wealth_learning;
        wealth_farming += other.wealth_farming;
        wealth_livestock += other.wealth_livestock;
        order += other.order;
        food += other.food;
        return *this;
    }

    Stats& operator-=(const Stats& other) {
        // counted 20 fields
        wealth_pct_all -= other.wealth_pct_all;
        wealth_pct_industry -= other.wealth_pct_industry;
        wealth_pct_mnfr -= other.wealth_pct_mnfr;
        wealth_pct_mining -= other.wealth_pct_mining;
        wealth_pct_agri -= other.wealth_pct_agri;
        wealth_pct_farming -= other.wealth_pct_farming;
        wealth_pct_com -= other.wealth_pct_com;
        wealth_pct_culture -= other.wealth_pct_culture;
        wealth_pct_fun -= other.wealth_pct_fun;
        wealth_subsistence -= other.wealth_subsistence;
        wealth_fun -= other.wealth_fun;
        wealth_mnfr -= other.wealth_mnfr;
        wealth_mari_com -= other.wealth_mari_com;
        wealth_local_com -= other.wealth_local_com;
        wealth_mining -= other.wealth_mining;
        wealth_learning -= other.wealth_learning;
        wealth_farming -= other.wealth_farming;
        wealth_livestock -= other.wealth_livestock;
        order -= other.order;
        food -= other.food;
        return *this;
    }
};
