#include <boost/range/join.hpp>
#include <boost/range/algorithm.hpp>
#include <boost/range/adaptor/transformed.hpp>
#include <boost/range/adaptors.hpp>
#include <boost/range/irange.hpp>
#include "province.hpp"
#include "province_vector_sliced.hpp"


inline ProvinceVectorSliced ConvertToVectorSliced(const ProvinceV& p_v) {
    ProvinceVectorSliced p(1+p_v.minor_regions.size(), CountPorts(p_v));
    p.major_head = p_v.capital[kHeadSlot];
    auto extract_slot = [](int slotIdx) {
        return [=](const MinorRegionArray &region) { return region[slotIdx]; };
    };
    auto p_v_minor_heads = boost::adaptors::transform(p_v.minor_regions, extract_slot(kHeadSlot));
    boost::range::copy(p_v_minor_heads, p.minor_heads().begin());

    auto p_v_maybe_minor_ports = boost::adaptors::transform(p_v.minor_regions, extract_slot(kPortSlot));
    auto p_v_maybe_all_ports = boost::join(std::array{p_v.capital[kPortSlot]}, p_v_maybe_minor_ports);
    auto p_v_ports = boost::adaptors::filter(p_v_maybe_all_ports, [](auto buildingIdx) {return buildingIdx != 0;});
    boost::range::copy(p_v_ports, p.ports().begin());

    auto p_v_major_other = boost::adaptors::slice(p_v.capital, kOtherStartSlot, p_v.capital.size());
    boost::range::copy(p_v_major_other, p.major_other().begin());

    for (auto i: boost::irange(p_v.minor_regions.size())) {
        auto& r = p_v.minor_regions[i];
        boost::range::copy(boost::adaptors::slice(r, kOtherStartSlot, r.size()), p.minor_other(i).begin());
    }
    return p;
}

inline ProvinceV ConvertToProvinceV(const ProvinceVectorSliced& pvs, const ProvinceV& pattern) {
    ProvinceV pv;
    auto port_idx = 0;
    pv.capital[kHeadSlot] = pvs.major_head;
    if (pattern.capital[kPortSlot] != 0) {
        pv.capital[kPortSlot] = pvs.ports()[port_idx++];
    }
    std::copy(pvs.major_other().begin(), pvs.major_other().end(), pv.capital.begin() + kOtherStartSlot);
    for (auto r_idx = 0; r_idx < pattern.minor_regions.size(); ++r_idx) {
        MinorRegionArray mr{};
        mr[kHeadSlot] = pvs.minor_heads()[r_idx];
        if (pattern.minor_regions[r_idx][kPortSlot] != 0) {
            mr[kPortSlot] = pvs.ports()[port_idx++];
        }
        auto pvs_minor_other = pvs.minor_other(r_idx);
        std::copy(pvs_minor_other.begin(), pvs_minor_other.end(), mr.begin() + kOtherStartSlot);
        pv.minor_regions.push_back(mr);
    }
    return pv;
}