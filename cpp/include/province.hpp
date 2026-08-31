#pragma once
#include <boost/format.hpp>
#include <ant/core/core.hpp>
#include "building_collection.hpp"
#include "math.hpp"


// 0 idx - Main building
// 1 idx - Port, can be Empty if Region is without a Port
using MinorRegionArray = std::array<short, 4>;
using MajorRegionArray = std::array<short, 6>;

constexpr int kHeadSlot = 0;
constexpr int kPortSlot = 1;
constexpr int kOtherStartSlot = 2;
constexpr int kEmptyBuildingIdx = 0;

constexpr int kMajorOtherSlotCount = 4;
constexpr int kMinorOtherSlotCount = 2;


template <int region_count>
struct Province {
    using MinorRegions = std::array<MinorRegionArray, region_count - 1>;

    MajorRegionArray capital{};
    MinorRegions minor_regions{};

    Stats stats;
};

struct ProvinceV {
    MajorRegionArray capital{};
    std::vector<MinorRegionArray> minor_regions{};
};

inline int CountPorts(const ProvinceV& p) {
    int count = 0;
    if (p.capital[kPortSlot] != 0) ++count;
    for (const auto& r: p.minor_regions) {
        if (r[kPortSlot] != 0) ++count;
    }
    return count;
}
