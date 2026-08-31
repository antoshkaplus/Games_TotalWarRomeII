#pragma once
#include <string>
#include <vector>
#include <unordered_map>
#include <jsoncpp/json/json.h>


struct Province {
    std::string id;
    std::string capital_region_id;
    std::vector<std::string> region_ids;
};


class Provinces {
    std::vector<Province> provinces;
    std::unordered_map<std::string, size_t> region_province;

    void init_region_province() {
        for (auto i = 0; i < provinces.size(); ++i) {
            for (auto& reg: provinces[i].region_ids) {
                region_province[reg] = i;
            }
        }
    }

public:
    Provinces() = default;
    explicit Provinces(std::vector<Province>&& provinces_arg) : provinces(std::move(provinces_arg)) {
        init_region_province();
    }
    explicit Provinces(const Json::Value& obj) {

    }

    void AddProvince(const Province& province) {
        auto idx = provinces.size();
        provinces.push_back(province);
        for (auto& reg: province.region_ids) {
            region_province[reg] = idx;
        }
    }

    Json::Value to_json() const {
        Json::Value res;
        for (auto& p : provinces) {
            Json::Value& obj = res.append(Json::Value{});
            obj["id"] = p.id;
            obj["capital_region_id"] = p.capital_region_id;
            Json::Value& regions_obj = obj["region_ids"];
            for (auto& r_id: p.region_ids) {
                regions_obj.append(r_id);
            }
        }
        return res;
    }
};