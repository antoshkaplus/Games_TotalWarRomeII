#pragma once
#include <yaml-cpp/yaml.h>
#include "building.hpp"
#include "stats_util.hpp"

inline std::vector<Building> read_buildings(const std::string& filename) {
    std::vector<Building> buildings;
    auto node = YAML::LoadFile(filename);
    for (const auto& item: node) {
        Building& building = buildings.emplace_back();
        building.name = item.first.Scalar();

        const auto& stats_node = item.second;
        building.stats = stats_from_node(stats_node);
        building.faction_stats = faction_stats_from_node(stats_node);

        if (stats_node["need_resource"]) {
            building.need_resource = stats_node["need_resource"].Scalar();
        }
        if (stats_node["parent"] && !stats_node["parent"].IsNull()) {
            building.parent = stats_node["parent"].Scalar();
        }
        if (stats_node["resource"]) {
            building.resource = stats_node["resource"].as<bool>();
        }
        if (stats_node["alias"]) {
            building.name_alias = stats_node["alias"].Scalar();
        }
    }
    return buildings;
}
