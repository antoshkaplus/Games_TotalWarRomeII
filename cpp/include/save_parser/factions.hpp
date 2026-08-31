#pragma once
#include <string>
#include <vector>
#include <unordered_map>


struct Faction {
    size_t idx;
    std::string id;
};


class Factions {
    std::unordered_map<size_t, std::string> id_by_idx_;
    std::unordered_map<std::string, size_t> idx_by_id_;

public:
    Factions(std::vector<Faction>& factions) {
        for (auto& fn: factions) {
            id_by_idx_[fn.idx] = fn.id;
            idx_by_id_[fn.id] = fn.idx;
        }
    }

    const std::string& id_by_idx(size_t idx) const {
        return id_by_idx_.at(idx);
    }

    size_t idx_by_id(const std::string& id) const {
        return idx_by_id_.at(id);
    }
};