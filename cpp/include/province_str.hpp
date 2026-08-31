#pragma once
#include <vector>
#include <string>
#include <boost/range/adaptors.hpp>
#include <boost/range/algorithm.hpp>
#include <ant/core/core.hpp>
#include "province_vector_sliced.hpp"
#include "building_collection.hpp"

inline std::vector<std::vector<std::string>> SplitProvinceStr(const std::string& str) {
    auto regions_str = ant::Split(str, '|');
    std::vector<std::vector<std::string>> rs(regions_str.size());
    auto tr = boost::adaptors::transform(regions_str, [](auto& str) { return ant::Split(str, ','); });
    boost::copy(tr, rs.begin());
    return rs;
}

inline std::string ProvinceStr(const ProvinceV& pr, const BuildingCollection& bc) {
    // need all names here, filter out zeros
    auto filter_out_empty = [](const auto& rng) {
        return boost::adaptors::filter(rng, [](auto buildingIdx) {return buildingIdx != 0;});
    };
    auto to_names = [&](const auto& rng) {
        return boost::adaptors::transform(rng, [&bc](auto buildingIdx) {return bc[buildingIdx].name;});
    };
    auto region_to_str = [&](const auto& rng) {
        auto names = to_names(filter_out_empty(rng));
        return ant::Join(names.begin(), names.end(), ",");
    };
    std::array capital{region_to_str(pr.capital)};
    auto regions_str = boost::join(capital, boost::adaptors::transform(pr.minor_regions, region_to_str));
    return ant::Join(regions_str.begin(), regions_str.end(), "|");
}

inline MajorRegionArray ParseCapital(const BuildingCollection& bc, const std::vector<std::string>& region_str) {
    MajorRegionArray c{};
    int i = kOtherStartSlot;
    for (const auto &s : region_str) {
        try {
            if (bc.IsPortBased(s)) {
                if (c[kPortSlot] != kEmptyBuildingIdx) {
                    throw std::invalid_argument("multiple ports per region");
                }
                c[kPortSlot] = bc.building_idx(s);
            } else if (bc.IsMajorHeadBased(s)) {
                if (c[kHeadSlot] != kEmptyBuildingIdx) {
                    throw std::invalid_argument("multiple heads per region");
                }
                c[kHeadSlot] = bc.building_idx(s);
            } else if (bc.IsMajorOther(s)) {
                if (i >= c.size()) {
                    throw std::invalid_argument("too many buildings");
                }
                c[i++] = bc.building_idx(s);
            } else {
                throw std::invalid_argument("unexpected building for region");
            }
        } catch (std::exception& e) {
            auto fmt = boost::format("failed to parse capital building '%1%'") % s;
            std::throw_with_nested(std::runtime_error(fmt.str()));
        }
    }
    return c;
}

inline MinorRegionArray ParseMinorRegion(const BuildingCollection& bc, const std::vector<std::string>& region_str) {
    try {
        MinorRegionArray c{};
        int i = kOtherStartSlot;
        for (const auto &s : region_str) {
            if (bc.IsPortBased(s)) {
                if (c[kPortSlot] != kEmptyBuildingIdx) {
                    throw std::invalid_argument("multiple ports per region");
                }
                c[kPortSlot] = bc.building_idx(s);
            } else if (bc.IsMinorHeadBased(s)) {
                if (c[kHeadSlot] != kEmptyBuildingIdx) {
                    throw std::invalid_argument("multiple heads per region");
                }
                c[kHeadSlot] = bc.building_idx(s);
            } else if (bc.IsMinorOther(s)) {
                if (i >= c.size()) {
                    throw std::invalid_argument("too many buildings");
                }
                c[i++] = bc.building_idx(s);
            } else {
                throw std::invalid_argument("unexpected building for region");
            }
        }
        return c;
    } catch (std::exception& e) {
        std::throw_with_nested(std::runtime_error("failed to parse minor region"));
    }
}

template <int region_count>
Province<region_count> ParseProvince(const BuildingCollection& bc, const std::array<std::vector<std::string>, region_count>& regions_str) {
    Province<region_count> p;
    p.capital = ParseCapital(bc, regions_str[0]);
    for (auto i = 1; i < regions_str.size(); ++i) {
        p.minor_regions[i-1] = ParseMinorRegion(bc, regions_str[i]);
    }
    p.stats += TotalStats(p.capital, bc.buildings());
    for (const auto& r : p.minor_regions) {
        p.stats += TotalStats(r, bc.buildings());
    }
    return p;
}

inline ProvinceV ParseProvince(const BuildingCollection& bc, const std::vector<std::vector<std::string>>& regions_str) {
    ProvinceV p;
    p.capital = ParseCapital(bc, regions_str[0]);
    for (auto i = 1; i < regions_str.size(); ++i) {
        p.minor_regions.emplace_back(ParseMinorRegion(bc, regions_str[i]));
    }
    return p;
}

inline ProvinceV ParseProvince(const BuildingCollection& bc, const std::string& regions_str) {
    auto split_regions = SplitProvinceStr(regions_str);
    return ParseProvince(bc, split_regions);
}