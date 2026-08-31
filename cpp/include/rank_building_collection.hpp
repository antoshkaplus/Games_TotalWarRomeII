#pragma once
#include "building_collection.hpp"

class RankBuildingCollection {
    const BuildingCollection& bc;
    int rank;

    // empty building does not have any leafs.
    // leafs return themselves
    std::vector<std::vector<int>> buildings_leafs_;

    std::vector<int> leafs_;
    std::vector<int> port_leafs_;
    std::vector<int> major_head_leafs_;
    std::vector<int> major_other_leafs_;
    std::vector<int> major_only_other_leafs_;
    std::vector<int> minor_head_leafs_;
    std::vector<int> minor_other_leafs_;
    std::vector<int> minor_only_other_leafs_;
    std::vector<int> common_other_leafs_;

    std::vector<int> TransformLeafs(const std::vector<int>& leafs) {
        std::set<int> new_leafs;
        for (auto i : leafs) {
            while (bc.building_rank(i) > rank) {
                if (!bc[i].parent) {
                    break;
                }
                i = bc.building_idx(bc[i].parent.value());
            }
            if (bc.building_rank(i) <= rank) new_leafs.insert(i);
        }
        return {new_leafs.begin(), new_leafs.end()};
    }

    void InitRankLeafs() {
        buildings_leafs_.resize(bc.buildings().size());
        for (auto i = 0; i < bc.buildings().size(); ++i) {
            buildings_leafs_[i] = (bc.building_rank(i) > rank ? std::vector{i} : TransformLeafs(bc.leafs(i)));
        }

        leafs_ = TransformLeafs(bc.Leafs());
        port_leafs_ = TransformLeafs(bc.PortLeafs());
        major_head_leafs_ = TransformLeafs(bc.MajorHeadLeafs());
        major_other_leafs_ = TransformLeafs(bc.MajorOtherLeafs());
        major_only_other_leafs_ = TransformLeafs(bc.MajorOnlyOtherLeafs());
        minor_head_leafs_ = TransformLeafs(bc.MinorHeadLeafs());
        minor_other_leafs_ = TransformLeafs(bc.MinorOtherLeafs());
        minor_only_other_leafs_ = TransformLeafs(bc.MinorOnlyOtherLeafs());
        common_other_leafs_ = TransformLeafs(bc.CommonOtherLeafs());
    }

public:
    RankBuildingCollection(const BuildingCollection& bc, int rank) : bc(bc), rank(rank) {
        InitRankLeafs();
    }

    const Building& operator[](int i) const {
        return bc[i] ;
    }

    const std::vector<Building>& buildings() const {
        return bc.buildings();
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
};