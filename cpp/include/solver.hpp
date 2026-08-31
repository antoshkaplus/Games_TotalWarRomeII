#pragma once

#include <yaml-cpp/yaml.h>
#include "building.hpp"
#include "stats.hpp"


using Int = int32_t;

std::vector<Building> read_buildings(const std::string& filename);
Stats stats_from_node(const YAML::Node& node);
YAML::Node stats_to_node(const Stats& stats);
std::vector<Int> Solve(int select_count, const std::vector<Building>& buildings);
void PrintSelection(const std::vector<Int>& selection, const std::vector<Building>& buildings);
std::vector<std::string> Split(std::string str, char delim);