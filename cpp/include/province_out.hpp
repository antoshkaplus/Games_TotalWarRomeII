#pragma once
#include "building_collection.hpp"
#include "province.hpp"
#include "province_vector_sliced.hpp"

inline void PrintRegion(std::span<const short> region, const BuildingCollection& bc) {
    for (auto i : region) {
        if (i == 0) {
            continue;
        }
        auto path = bc.path(bc[i].name);
        auto path_str = ant::Join(path.begin(), path.end(), " -> ");
        ant::Println(std::cout, path_str);
    }
}

inline void PrintRegion(std::span<const int> region, const BuildingCollection& bc) {
    for (auto i : region) {
        if (i == 0) {
            continue;
        }
        auto path = bc.path(bc[i].name);
        auto path_str = ant::Join(path.begin(), path.end(), " -> ");
        ant::Println(std::cout, path_str);
    }
}

template<int region_count>
void PrintProvince(const Province<region_count>& province, const BuildingCollection& bc) {
    try {
        const auto &s = province.stats;
        auto f = boost::format("Province: wealth: %1%, order: %2%, food: %3%")
                 % s.wealth() % s.order % s.food;
        ant::Println(std::cout, f);
        ant::Println(std::cout, "Capital");
        PrintRegion(province.capital, bc);
        for (auto r_i = 0; r_i < province.minor_regions.size(); ++r_i) {
            ant::Println(std::cout, "Minor ", r_i);
            PrintRegion(province.minor_regions[r_i], bc);
        }
    } catch (std::exception& e) {
        std::throw_with_nested(std::runtime_error("error while printing province"));
    }
}

inline void Print(const ProvinceVectorSliced& p, const BuildingCollection& bc) {
    PrintRegion(std::array<int, 1>{p.major_head}, bc);
    PrintRegion(p.data, bc);
}