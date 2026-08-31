#pragma once
#include "building.hpp"
#include "stats.hpp"
#include "province_vector_sliced.hpp"

inline Stats TotalStats(const std::vector<int>& selection, const std::vector<Building>& buildings) {
    Stats res;
    for (const auto& s : selection) {
        res += buildings[s].stats;
    }
    return res;
}

inline Stats TotalStats(const std::span<short const> selection, const std::vector<Building>& buildings) {
    Stats res;
    for (const auto& s : selection) {
        res += buildings[s].stats;
    }
    return res;
}

inline Stats TotalStats(const ProvinceVectorSliced& pr, const std::vector<Building>& buildings) {
    auto st = buildings[pr.major_head].stats;
    return st += TotalStats(pr.data, buildings);
}