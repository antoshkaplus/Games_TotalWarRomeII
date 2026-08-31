#pragma once
#include "math.hpp"
#include "province.hpp"

inline uint64_t CountEmptyCapitalCandidates(const BuildingCollection& bc, bool hasPort) {
    return bc.MajorHeadLeafs().size() * (hasPort * bc.PortLeafs().size()) * CombinationsCount(4, bc.MajorOtherLeafs().size());
}

inline uint64_t CountEmptyMajorWithOneMinorCandidates(const BuildingCollection& bc, bool majorHasPort, bool minorHasPort) {
    uint64_t count = bc.MajorHeadLeafs().size() * bc.MinorHeadLeafs().size() * CombinationsCount(majorHasPort + minorHasPort, bc.PortLeafs().size());
    uint64_t other_count_total = 0;
    for (int i = 0; i < kMajorOtherSlotCount; ++i) {
        uint64_t other_count = CombinationsCount(i, bc.MajorOnlyOtherLeafs().size());
        for (int j = 0; j < kMinorOtherSlotCount; ++j) {
            other_count *= CombinationsCount(j, bc.MinorOnlyOtherLeafs().size());
            auto major_common_other_slots = kMajorOtherSlotCount - i;
            auto minor_common_other_slots = kMinorOtherSlotCount - j;
            // common same buildings per candidate
            for (int k = 0; k <= std::min(major_common_other_slots, minor_common_other_slots); ++k) {
                other_count *= CombinationsCount(k, bc.CommonOtherLeafs().size());
                other_count *= CombinationsCount(major_common_other_slots + minor_common_other_slots - 2*k, bc.CommonOtherLeafs().size() - k);
            }
        }
        other_count_total += other_count;
    }
    count *= other_count_total;
    return count;
}