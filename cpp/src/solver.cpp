#include <iostream>
#include <optional>
#include <numeric>
#include <boost/math/special_functions/factorials.hpp>
#include "solver.hpp"
#include "stats.hpp"
#include "math.hpp"
#include "province_stats.hpp"

Stats stats_from_node(const YAML::Node& node) {
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

YAML::Node stats_to_node(const Stats& stats) {
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

std::vector<Int> Solve(int select_count, const std::vector<Building>& buildings) {
    std::vector<Int> selection(select_count);
    std::iota(selection.begin(), selection.end(), 0);

    double max_wealth = 0;
    std::vector<Int> max_wealth_selection;
    for (;;) {
        auto total_stats = std::accumulate(selection.begin(), selection.end(), Stats(), [&](Stats total, Int i) {
            return total += buildings[i].stats;
        });
        auto wealth = total_stats.wealth();
        if (wealth > max_wealth) {
            max_wealth = wealth;
            max_wealth_selection = selection;
        }
        if (!NextCombination(selection, buildings.size())) break;
    }
    return max_wealth_selection;
}

void PrintSelection(const std::vector<Int>& selection, const std::vector<Building>& buildings) {
    const auto stats = TotalStats(selection, buildings);
    std::cout << stats.wealth() << std::endl;
    for (const auto i : selection) {
        std::cout << buildings[i].name << ", ";
    }
    std::cout << std::endl;
}

std::vector<std::string> Split(std::string str, char delim) {
    std::vector<std::string> r;
    int s_i = 0; // starting index for sustr
    for (int i = 0; i < str.size(); ++i) {
        if (str[i] == delim) {
            r.push_back(str.substr(s_i, i-s_i));
            s_i = i+1;
        }
    }
    r.push_back(str.substr(s_i));
    return r;
}