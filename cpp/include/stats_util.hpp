#pragma once
#include <yaml-cpp/yaml.h>
#include "stats.hpp"
#include "bonus_stats.hpp"

inline Stats stats_from_node(const YAML::Node& node) {
    Stats stats {
        .wealth_pct_all = node["wealth_pct_all"] ? node["wealth_pct_all"].as<int>() : 0,
        .wealth_pct_industry = node["wealth_pct_industry"] ? node["wealth_pct_industry"].as<int>() : 0,
        .wealth_pct_mnfr = node["wealth_pct_mnfr"] ? node["wealth_pct_mnfr"].as<int>() : 0,
        .wealth_pct_mining = node["wealth_pct_mining"] ? node["wealth_pct_mining"].as<int>() : 0,
        .wealth_pct_agri = node["wealth_pct_agri"] ? node["wealth_pct_agri"].as<int>() : 0,
        .wealth_pct_farming = node["wealth_pct_farming"] ? node["wealth_pct_farming"].as<int>() : 0,
        .wealth_pct_com = node["wealth_pct_com"] ? node["wealth_pct_com"].as<int>() : 0,
        .wealth_pct_culture = node["wealth_pct_culture"] ? node["wealth_pct_culture"].as<int>() : 0,
        .wealth_pct_fun = node["wealth_pct_fun"] ? node["wealth_pct_fun"].as<int>() : 0,
        .wealth_subsistence = node["wealth_subsistence"] ? node["wealth_subsistence"].as<int>() : 0,
        .wealth_fun = node["wealth_fun"] ? node["wealth_fun"].as<int>() : 0,
        .wealth_mnfr = node["wealth_mnfr"] ? node["wealth_mnfr"].as<int>() : 0,
        .wealth_mari_com = node["wealth_mari_com"] ? node["wealth_mari_com"].as<int>() : 0,
        .wealth_local_com = node["wealth_local_com"] ? node["wealth_local_com"].as<int>() : 0,
        .wealth_mining = node["wealth_mining"] ? node["wealth_mining"].as<int>() : 0,
        .wealth_learning = node["wealth_learning"] ? node["wealth_learning"].as<int>() : 0,
        .wealth_farming = node["wealth_farming"] ? node["wealth_farming"].as<int>() : 0,
        .wealth_livestock = node["wealth_livestock"] ? node["wealth_livestock"].as<int>() : 0,
        .order = node["order"] ? node["order"].as<int>() : 0,
        .food = node["food"] ? node["food"].as<int>() : 0,
    };
    return stats;
}

inline Stats faction_stats_from_node(const YAML::Node& node) {
    Stats stats {
        .wealth_pct_mnfr = node["wealth_pct_mnfr_faction"] ? node["wealth_pct_mnfr_faction"].as<int>() : 0,
        .wealth_pct_mining = node["wealth_pct_mining_faction"] ? node["wealth_pct_mining_faction"].as<int>() : 0,
        .wealth_pct_agri = node["wealth_pct_agri_faction"] ? node["wealth_pct_agri_faction"].as<int>() : 0,
        .wealth_pct_com = node["wealth_pct_com_faction"] ? node["wealth_pct_com_faction"].as<int>() : 0,
        .order = node["order_faction"] ? node["order_faction"].as<int>() : 0,
    };
    return stats;
}

inline BonusStats bonus_stats_from_node(const YAML::Node& node) {
    BonusStats stats {
            .wealth_pct_industry = node["wealth_pct_industry"] ? node["wealth_pct_industry"].as<int>() : 0,
    };
    return stats;
}

inline YAML::Node stats_to_node(const Stats& stats) {
    YAML::Node node;
    // counted 20 fields.
    node["wealth_pct_all"] = stats.wealth_pct_all;
    node["wealth_pct_industry"] = stats.wealth_pct_industry;
    node["wealth_pct_mnfr"] = stats.wealth_pct_mnfr;
    node["wealth_pct_mining"] = stats.wealth_pct_mining;
    node["wealth_pct_agri"] = stats.wealth_pct_agri;
    node["wealth_pct_farming"] = stats.wealth_pct_farming;
    node["wealth_pct_com"] = stats.wealth_pct_com;
    node["wealth_pct_culture"] = stats.wealth_pct_culture;
    node["wealth_pct_fun"] = stats.wealth_pct_fun;
    node["wealth_subsistence"] = stats.wealth_subsistence;
    node["wealth_fun"] = stats.wealth_fun;
    node["wealth_mnfr"] = stats.wealth_mnfr;
    node["wealth_mari_com"] = stats.wealth_mari_com;
    node["wealth_local_com"] = stats.wealth_local_com;
    node["wealth_mining"] = stats.wealth_mining;
    node["wealth_learning"] = stats.wealth_learning;
    node["wealth_farming"] = stats.wealth_farming;
    node["wealth_livestock"] = stats.wealth_livestock;
    node["order"] = stats.order;
    node["food"] = stats.food;
    return node;
}

inline void PrintStats(const Stats& stats) {
    ant::Println(std::cout, "wealth: ", stats.wealth(), ", food: ", stats.food, ", order: ", stats.order);
}

Stats operator+(Stats stats, BonusStats bonus_stats) {
    stats.wealth_pct_industry += bonus_stats.wealth_pct_industry;
    return stats;
}