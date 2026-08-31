#pragma once
#include <set>
#include <string>
#include <optional>
#include "province.hpp"
#include "building_collection.hpp"
#include <yaml-cpp/yaml.h>

struct ProfileProvince {
    std::string name;
    std::optional<std::string> alias;
    std::string province_str;
};

struct ProfileConstraints {
    int province_order;
    int total_food;
};

// Profile is needed to keep track of users provinces during actual game.
// It's easier to change things and work with them when in structured form.
class Profile {
    BonusStats tech_bonus_stats_;
    //std::set<std::string> banned_buildings;
    std::vector<ProfileProvince> provinces;
    // map province name/alias to index
    std::unordered_map<std::string, int> province_idx;

public:
    void Add(ProfileProvince&& pr) {
        auto idx = provinces.size();
        province_idx[pr.name] = idx;
        if (pr.alias) {
            province_idx[pr.alias.value()] = idx;
        }
        provinces.emplace_back(std::move(pr));
    }

    const ProfileProvince& operator[](std::string province_id) const {
        try {
            return provinces.at(province_idx.at(province_id));
        } catch (std::exception& e) {
            auto fmt = boost::format("failed to province %1% in profile") % province_id;
            std::throw_with_nested(std::runtime_error(fmt.str()));
        }
    }

    BonusStats& tech_bonus_stats() {
        return tech_bonus_stats_;
    }
};

inline Profile read_profile(const std::string& filename) {
    Profile profile;
    auto root_node = YAML::LoadFile(filename);
    profile.tech_bonus_stats() = bonus_stats_from_node(root_node["TechBonusStats"]);
    for (const auto &pr: root_node["Provinces"]) {
        ProfileProvince profile_pr;
        profile_pr.name = pr.first.Scalar();
        if (pr.second["Alias"]) {
            profile_pr.alias = pr.second["Alias"].Scalar();
        }
        if (pr.second["Regions"]) {
            profile_pr.province_str = pr.second["Regions"].Scalar();
        }
        profile.Add(std::move(profile_pr));
    }
    return profile;
}

//    auto node = YAML::LoadFile(filename);
//    for (const auto& item: node) {
//        Building& building = buildings.emplace_back();
//        building.name = item.first.Scalar();
//
//        const auto& stats_node = item.second;
//        building.stats = stats_from_node(stats_node);
//
//        if (stats_node["need_resource"]) {
//            building.need_resource = stats_node["need_resource"].Scalar();
//        }
//        if (stats_node["parent"] && !stats_node["parent"].IsNull()) {
//            building.parent = stats_node["parent"].Scalar();
//        }
//        if (stats_node["resource"]) {
//            building.resource = stats_node["resource"].as<bool>();
//        }
//        if (stats_node["alias"]) {
//            building.name_alias = stats_node["alias"].Scalar();
//        }
//    }
//    return buildings;
