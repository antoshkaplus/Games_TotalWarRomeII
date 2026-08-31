#pragma once
#include <boost/log/trivial.hpp>
#include "province.hpp"
#include "leaf_building_collection.hpp"
#include "ga.hpp"

struct ProvinceVectorSliced {
    std::vector<int> data;
    int major_head = 0;
    // minor heads start at zero and then ports.
    int start_ports;
    int start_major_other;
    int start_minor_other;

    ProvinceVectorSliced() {}

    ProvinceVectorSliced(int region_count, int port_count) :
        data(region_count-1 + port_count + kMajorOtherSlotCount + (region_count-1)*kMinorOtherSlotCount),
        start_ports(region_count-1),
        start_major_other(region_count-1 + port_count),
        start_minor_other(region_count-1 + port_count + kMajorOtherSlotCount) {

        BOOST_LOG_TRIVIAL(trace) << "ProvinceVectorSliced " << "start_ports:" << start_ports << " start_major_other: " << start_major_other
                                 << " start_minor_other: " << start_minor_other << " size: " << data.size();
    }

    std::span<int> minor_heads() {
        return std::span(data.begin(), data.begin()+start_ports);
    }
    std::span<const int> minor_heads() const {
        return std::span(data.begin(), data.begin()+start_ports);
    }

    std::span<int> ports() {
        return std::span(data.begin()+start_ports, data.begin()+start_major_other);
    }
    std::span<const int> ports() const {
        return std::span(data.begin()+start_ports, data.begin()+start_major_other);
    }

    std::span<int> major_other() {
        return std::span(data.begin()+start_major_other, data.begin()+start_minor_other);
    }
    std::span<const int> major_other() const {
        return std::span(data.begin()+start_major_other, data.begin()+start_minor_other);
    }

    std::span<int> minor_other() {
        return std::span(data.begin()+start_minor_other, data.end());
    }

    std::span<int> minor_other(int i) {
        auto begin = data.begin()+start_minor_other+i*kMinorOtherSlotCount;
        return std::span(begin, begin+kMinorOtherSlotCount);
    }
    std::span<const int> minor_other(int i) const {
        auto begin = data.begin()+start_minor_other+i*kMinorOtherSlotCount;
        return std::span(begin, begin+kMinorOtherSlotCount);
    }
};

template <LeafBuildingCollection Collection>
inline ProvinceVectorSliced RandomProvince(const Collection& bc, int region_count, int port_count) {
    ProvinceVectorSliced p(region_count, port_count);
    ga::RandomLeafs leafs;
    p.major_head = leafs.Random(bc.MajorHeadLeafs());
    for (auto& b : p.minor_heads()) {
        b = leafs.Random(bc.MinorHeadLeafs());
    }
    for (auto& b : p.ports()) {
        b = leafs.Random(bc.PortLeafs());
    }
    for (auto& b : p.major_other()) {
        for (;;) {
            auto r = leafs.Random(bc.MajorOtherLeafs());
            if (!std::count(p.major_other().begin(), p.major_other().end(), r)) {
                b = r;
                break;
            }
        }
    }
    for (auto i = p.start_minor_other; i < p.data.size(); i+=2) {
        while((p.data[i] = leafs.Random(bc.MinorOtherLeafs())) ==
              (p.data[i+1] = leafs.Random(bc.MinorOtherLeafs())));
    }
    return p;
}

template <LeafBuildingCollection Collection>
inline ProvinceVectorSliced RandomProvinceWithPattern(const Collection& bc, const ProvinceVectorSliced& pattern) {
    ProvinceVectorSliced p = pattern;
    ga::RandomLeafs leafs;
    auto random = [&](auto buildingIdx, const std::vector<int>& on_empty_leafs) {
        if (buildingIdx == 0) {
            return leafs.Random(on_empty_leafs);
        }
        return leafs.Random(bc.leafs(buildingIdx));
    };

    p.major_head = random(p.major_head, bc.MajorHeadLeafs());
    for (auto& b : p.minor_heads()) {
        b = random(b, bc.MinorHeadLeafs());
    }
    for (auto& b : p.ports()) {
        b = random(b, bc.PortLeafs());
    }
    for (auto& b : p.major_other()) {
        auto old_b = b;
        b = 0; // to pass duplicates check
        for (;;) {
            auto r = random(old_b, bc.MajorOtherLeafs());
            if (!std::count(p.major_other().begin(), p.major_other().end(), r)) {
                b = r;
                break;
            }
        }
    }
    for (auto i = p.start_minor_other; i < p.data.size(); i+=2) {
        auto& b_1 = p.data[i];
        auto& b_2 = p.data[i+1];
        auto old_b_1 = b_1;
        auto old_b_2 = b_2;
        while((b_1 = random(old_b_1, bc.MinorOtherLeafs())) ==
              (b_2 = random(old_b_2, bc.MinorOtherLeafs())));
    }
    return p;
}
