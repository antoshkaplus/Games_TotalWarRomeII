#pragma once
#include <ant/core/core.hpp>
#include "building.hpp"
#include "leaf_building_collection.hpp"

class BuildingCollection {
    std::vector<Building> buildings_;
    std::vector<int> building_ranks_;
    // map name/alias name to building index
    std::unordered_map<std::string, int> buildings_idx_;
    std::unordered_map<int, int> buildings_root_;
    // empty building does not have any leafs.
    // leafs return themselves
    std::unordered_map<int, std::vector<int>> buildings_leafs_;

    std::vector<int> leafs_;
    std::vector<int> port_leafs_;
    std::vector<int> major_head_leafs_;
    std::vector<int> major_other_leafs_;
    std::vector<int> major_only_other_leafs_;
    std::vector<int> minor_head_leafs_;
    std::vector<int> minor_other_leafs_;
    std::vector<int> minor_only_other_leafs_;
    std::vector<int> common_other_leafs_;


    void InitBuildingsIdx() {
        for (auto i = 0; i < buildings_.size(); ++i) {
            buildings_idx_[buildings_[i].name] = i;
            if (buildings_[i].name_alias) {
                buildings_idx_[buildings_[i].name_alias.value()] = i;
            }
        }
    }

    int FindBuildingRoot(int building_idx) const {
        std::set<int> building_idx_path {building_idx};
        while (buildings_[building_idx].parent) {
            auto parent_name = buildings_[building_idx].parent.value();
            building_idx = this->buildings_idx_.at(parent_name);
            if (!building_idx_path.insert(building_idx).second) {
                auto s = ant::Join(building_idx_path.begin(), building_idx_path.end(), ", ");
                auto fmt = boost::format("circular hierarchy: %1%; closing idx: %2%") % s % building_idx;
                throw std::runtime_error(fmt.str());
            }
        }
        return building_idx;
    }

    void InitBuildingsRoot() {
        for (auto i = 0; i < buildings_.size(); ++i) {
            try {
                buildings_root_[i] = FindBuildingRoot(i);
            } catch (std::exception& e) {
                auto fmt = boost::format("failed to find building root for %1% (%2%)")
                         % i % buildings_[i].name;
                std::throw_with_nested(std::runtime_error(fmt.str()));
            }
        }
    }

    std::set<std::string> ComputeParents() const {
        std::set<std::string> parents;
        for (auto i = 0; i < buildings_.size(); ++i) {
            if (buildings_[i].parent) {
                parents.insert(buildings_[i].parent.value());
            }
        }
        return parents;
    }

    void InitBuildingsLeafs() {
        for (auto i = 0; i < buildings_.size(); ++i) {
            buildings_leafs_[i] = FindLeafs(i);
            if (i > 0 && buildings_leafs_[i].size() == 0) {
                buildings_leafs_[i].push_back(i);
            }
        }
    }

    void InitLeafs() {
        auto parents = ComputeParents();
        for (auto i = 0; i < buildings_.size(); ++i) {
            const auto& name = buildings_[i].name;
            // we don't consider resources for now.
            if (buildings_[i].resource) {
                continue;
            }

            if (parents.count(name) == 0) {
                leafs_.push_back(i);

                // don't consider Empty Building
                if (i == 0) continue;

                if (IsPortBased(name)) {
                    port_leafs_.push_back(i);
                } else if (IsMajorHeadBased(name)) {
                    major_head_leafs_.push_back(i);
                }  else if (IsMinorHeadBased(name)) {
                    minor_head_leafs_.push_back(i);
                } else {
                    if (IsMajorOther(name)) {
                        major_other_leafs_.push_back(i);
                    }
                    if (IsMinorOther(name)) {
                        minor_other_leafs_.push_back(i);
                    }
                    if (IsMinorOther(name) && !IsMajorOther(name)) {
                        minor_only_other_leafs_.push_back(i);
                    }
                    if (IsMajorOther(name) && !IsMinorOther(name)) {
                        major_only_other_leafs_.push_back(i);
                    }
                    if (IsMinorOther(name) && IsMajorOther(name)) {
                        common_other_leafs_.push_back(i);
                    }
                }
            }
        }
    }

    void InitBuildingRanks() {
        building_ranks_.resize(buildings_.size());
        for (auto i = 0; i < buildings_.size(); ++i) {
            building_ranks_[i] = path(buildings_[i].name).size();
        }
    }

    std::vector<int> FindLeafs(int building_idx) {
        std::vector<int> leafs;
        std::vector<int> children = {building_idx};
        while (!children.empty()) {
            std::vector<int> new_children;
            for (auto i : children) {
                auto new_children_found = false;
                for (int k = 0; k < buildings_.size(); ++k) {
                    if (buildings_[k].parent && buildings_[k].parent.value() == buildings_[i].name) {
                        new_children.push_back(k);
                        new_children_found = true;
                    }
                }
                if (!new_children_found) {
                    leafs.push_back(i);
                }
            }
            children = new_children;
        }
        return leafs;
    }

public:
    BuildingCollection() = default;
    BuildingCollection(const std::vector<Building>& buildings) : buildings_(buildings) {
        try {
            InitBuildingsIdx();
            InitBuildingRanks();
            InitBuildingsRoot();
            InitBuildingsLeafs();
            InitLeafs();
        } catch (std::exception& e) {
            std::throw_with_nested(std::runtime_error("failed to create BuildingCollection"));
        }
    }

    int building_idx(const std::string& building_name) const {
        try {
            return buildings_idx_.at(building_name);
        } catch (std::exception& e) {
            auto fmt = boost::format("no building name '%1%' found in BuildingCollection") % building_name;
            std::throw_with_nested(std::runtime_error(fmt.str()));
        }
    }

    int building_rank(const std::string& building_name) const {
        return building_ranks_[building_idx(building_name)];
    }

    int building_rank(int i) const {
        return building_ranks_[i];
    }

    const Building& operator[](int i) const {
        return buildings_.at(i);
    }

    const std::vector<Building>& buildings() const {
        return buildings_;
    }

    std::vector<std::string> find_leafs(const std::string& building_name) {
        auto idx = building_idx(building_name);
        auto leafs_idx = FindLeafs(idx);
        std::vector<std::string> leafs;
        for (auto idx : leafs_idx) {
            leafs.push_back(buildings_[idx].name);
        }
        return leafs;
    }

    bool IsPortBased(const std::string& building_name) const {
        auto idx = building_idx(building_name);
        return buildings_root_.at(idx) == building_idx("Port");
    }

    bool IsMajorHeadBased(const std::string& building_name) const {
        auto idx = building_idx(building_name);
        return buildings_root_.at(idx) == building_idx("Settlement");
    }

    bool IsMajorOther(const std::string& building_name) const {
        auto idx = building_idx(building_name);
        return buildings_root_.at(idx) != building_idx("Well") && buildings_root_.at(idx) != building_idx("Pit Mine");
    }

    bool IsMajorOnlyOther(const std::string& building_name) const {
        auto idx = building_idx(building_name);
        return buildings_root_.at(idx) == building_idx("Commons") || buildings_root_.at(idx) == building_idx("Warrior Lodge");
    }

    bool IsMinorHeadBased(const std::string& building_name) const {
        auto idx = building_idx(building_name);
        return buildings_[idx].resource || buildings_root_.at(idx) == building_idx("Farmstead");
    }

    bool IsMinorOther(const std::string& building_name) const {
        auto idx = building_idx(building_name);
        return buildings_root_.at(idx) != building_idx("Commons") && buildings_root_.at(idx) != building_idx("Warrior Lodge");
    }

    bool IsMinorOnlyOther(const std::string& building_name) const {
        auto idx = building_idx(building_name);
        return buildings_root_.at(idx) == building_idx("Well") || buildings_root_.at(idx) == building_idx("Pit Mine");
    }

    bool IsCommonOther(const std::string& building_name) const {
        return !IsMajorOnlyOther(building_name) && !IsMinorOnlyOther(building_name);
    }

    const std::vector<int>& leafs(int buildingIdx) const {
        return buildings_leafs_.at(buildingIdx);
    }

    const std::vector<int>& Leafs() const {
        return leafs_;
    }

    const std::vector<int>& PortLeafs() const {
        return port_leafs_;
    }

    const std::vector<int>& MajorHeadLeafs() const {
        return major_head_leafs_;
    }

    const std::vector<int>& MajorOtherLeafs() const {
        return major_other_leafs_;
    }

    const std::vector<int>& MinorHeadLeafs() const {
        return minor_head_leafs_;
    }

    const std::vector<int>& MinorOtherLeafs() const {
        return minor_other_leafs_;
    }

    const std::vector<int>& MajorOnlyOtherLeafs() const {
        return major_only_other_leafs_;
    }

    const std::vector<int>& MinorOnlyOtherLeafs() const {
        return minor_only_other_leafs_;
    }

    const std::vector<int>& CommonOtherLeafs() const {
        return common_other_leafs_;
    }

    // building path root to the provided building
    std::vector<std::string> path(const std::string& building_name) const {
        std::vector<std::string> p = {building_name};
        for (;;) {
            auto idx = building_idx(p.back());
            const auto& parent = buildings_[idx].parent;
            if (!parent) {
                return p;
            }
            p.push_back(parent.value());
        }
    }
};
