#pragma once

#include <chrono>
#include "province.hpp"
#include "building_collection.hpp"

namespace ga {

// can be optimized further
using ProvinceVector = std::vector<int>;
using EmptySlots = std::vector<int>;

// smallest goes first
inline std::vector<int> ComputeBuildingsOrder(const BuildingCollection& bc) {
    std::vector<int> order;
    for (auto i = 0; i < bc.buildings().size(); ++i) {
        const auto& name = bc[i].name;
        if (bc.IsMajorHeadBased(name)) {
            order.push_back(0);
        } else if (bc.IsMinorHeadBased(name)) {
            order.push_back(1);
        } else if (bc.IsPortBased(name)) {
            order.push_back(2);
        } else if (bc.IsMajorOnlyOther(name)) {
            order.push_back(3);
        } else if (bc.IsMinorOnlyOther(name)) {
            order.push_back(4);
        } else {
            // Common Other
            order.push_back(5);
        }
    }
    return order;
}

class BuildingsLess {
    const std::vector<int>& order;

public:
    BuildingsLess(const std::vector<int>& order) : order(order) {}

    bool operator()(int i, int j) const {
        return order[i] < order[j] || (order[i] == order[j] && i < j);
    }
};

class RandomLeafs {
    std::default_random_engine rng{static_cast<uint64_t>(std::chrono::system_clock::now().time_since_epoch().count())};
    std::uniform_int_distribution<int> distr;

public:
    RandomLeafs() {}

    int Random(const std::vector<int>& leafs) {
        return leafs[distr(rng) % leafs.size()];
    }

    int Random(int max) {
        return distr(rng) % max;
    }
};

inline bool AddRandomLeafs(const std::vector<int>& leafs, RandomLeafs& random_leafs,
                    ProvinceVector& province, int add_count, EmptySlots& empty_slots) {
    auto start_idx = province.size();
    for (auto i = 0; i < add_count; ++i) {
        province.push_back(random_leafs.Random(leafs));
    }
    std::sort(province.begin()+start_idx, province.end());

    int prev = province[start_idx];
    int count = 1;
    for (int i = start_idx+1; i <= province.size(); ++i) {
        if (i == province.size() || prev != province[i]) {
            if (empty_slots.size() < count) return false;
            for (auto k = 0; k < count; ++k) {
                --empty_slots[k];
            }
            std::sort(empty_slots.rbegin(), empty_slots.rend());
            std::erase(empty_slots, 0);

            if (i == province.size()) break;

            count = 1;
            prev = province[i];
            continue;
        }
        ++count;
    }
    return true;
}

inline void AddUniqueLeafs(const std::vector<int>& leafs, ProvinceVector& province, int add_count) {
    std::vector<int> items = leafs;
    std::default_random_engine rng(std::chrono::system_clock::now().time_since_epoch().count());
    std::shuffle(items.begin(), items.end(), rng);
    items.resize(add_count);
    province.insert(province.end(), items.begin(), items.end());
}

inline std::vector<ProvinceVector> MakePopulation(const BuildingCollection& bc, int region_count, int port_count, int population_count) {
    RandomLeafs random_leafs;
    std::vector<ProvinceVector> population(population_count);
    for (auto i = 0; i < population_count; ++i) {
        for (;;) {
            auto &s = population[i] = {};
            s.push_back(random_leafs.Random(bc.MajorHeadLeafs()));
            for (auto i = 0; i < region_count-1; ++i) {
                s.push_back(random_leafs.Random(bc.MinorHeadLeafs()));
            }
            for (auto i = 0; i < port_count; ++i) {
                s.push_back(random_leafs.Random(bc.PortLeafs()));
            }

            int major_only_count = random_leafs.Random(kMajorOtherSlotCount);
            AddUniqueLeafs(bc.MajorOnlyOtherLeafs(), s, major_only_count);

            // Major empty slots will add later
            EmptySlots empty_slots(region_count - 1, kMinorOtherSlotCount);
            int minor_only_count = random_leafs.Random((region_count - 1) * kMinorOtherSlotCount);
            if (!AddRandomLeafs(bc.MinorOnlyOtherLeafs(), random_leafs, s, minor_only_count, empty_slots)) {
                continue;
            }

            if (kMajorOtherSlotCount - major_only_count > 0) {
                empty_slots.push_back(kMajorOtherSlotCount - major_only_count);
                std::sort(empty_slots.rbegin(), empty_slots.rend());
            }
            int total_slots = std::accumulate(empty_slots.begin(), empty_slots.end(), 0);
            if (!AddRandomLeafs(bc.CommonOtherLeafs(), random_leafs, s, total_slots, empty_slots)) {
                continue;
            }

            if (s.size() != region_count + port_count + kMajorOtherSlotCount + (region_count-1)*kMinorOtherSlotCount) {
                throw std::runtime_error("Unexpected building count in a province.");
            }

            break;
        }
    }
    return population;
}

//ProvinceVector Solve(const BuildingCollection& bc, int region_count, int port_count, const Constraints& constraints, int population_count) {
//    auto population = MakePopulation(bc, region_count, port_count, population_count);
//    std::erase_if(population, [](const auto& p) {
//        s = TotalStats(p, bc.buildings());
//        return s.food < constraints.min_food || s.order < constraints.min_order;
//    })
//
//    auto p = *ant::MaxElement(population.begin(), population.end(), [&](const auto& p) {
//        return TotalStats(p, bc.buildings()).wealth();
//    });
//
//    return p;
//}

}