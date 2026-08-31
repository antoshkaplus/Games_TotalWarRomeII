#pragma once
#include <boost/log/trivial.hpp>
#include "province_vector_sliced.hpp"
#include "score.hpp"
#include "province_stats.hpp"
#include "leaf_building_collection.hpp"
#include "bonus_stats.hpp"

template <LeafBuildingCollection Collection>
class LocalSearch {
    ProvinceVectorSliced& p;
    const ProvinceVectorSliced& pattern;
    const Collection& bc;
    const Score& score;
    Stats stats;

    void ReplaceBuilding(int& slot, int newBuildingIdx) {
        try {
            stats -= bc[slot].stats;
            slot = newBuildingIdx;
            stats += bc[newBuildingIdx].stats;
        } catch (std::exception& e) {
            auto fmt = boost::format("ReplaceBuilding");
            std::throw_with_nested(std::runtime_error(fmt.str()));
        }
    }

public:
    LocalSearch(ProvinceVectorSliced& p, const ProvinceVectorSliced& pattern, const Collection& bc, const Score& score, BonusStats bonus_stats = BonusStats{})
        : p(p), pattern(pattern), bc(bc), score(score) {
        stats = TotalStats(p, bc.buildings()) + bonus_stats;
    }

    std::optional<int> ImproveBuilding(int current, const std::vector<int>& options, Stats s) {
        try {
            double start_score = score(s);
            int best_building_idx = current;
            double best_score = score(s);
            s -= bc[current].stats;
            for (auto b : options) {
                s += bc[b].stats;
                if (best_score < score(s)) {
                    best_score = score(s);
                    best_building_idx = b;
                }
                s -= bc[b].stats;
            }
            if (best_score - start_score > 1e-6) {
                return best_building_idx;
            }
            return {};
        } catch (std::exception& e) {
            auto fmt = boost::format("failed to improve building %1%") % current;
            std::throw_with_nested(std::runtime_error(fmt.str()));
        }
    }

    std::optional<int> ImproveBuilding(int current, const std::vector<int>& options,
                                       std::span<int> current_set, Stats s) {
        try {
            double start_score = score(s);
            int best_building_idx = current;
            double best_score = score(s);
            s -= bc[current].stats;
            for (auto b : options) {
                if (std::find(current_set.begin(), current_set.end(), b) != current_set.end()) {
                    continue;
                }
                s += bc[b].stats;
                if (best_score < score(s)) {
                    best_score = score(s);
                    best_building_idx = b;
                }
                s -= bc[b].stats;
            }
            if (best_score - start_score > 1e-6) {
                return best_building_idx;
            }
            return {};
        } catch (std::exception& e) {
            auto fmt = boost::format("failed to improve building %1%") % current;
            std::throw_with_nested(std::runtime_error(fmt.str()));
        }
    }

    void ImproveMajorHead() {
        auto& leafs = pattern.major_head == 0 ? bc.MajorHeadLeafs() : bc.leafs(pattern.major_head);
        auto res = ImproveBuilding(p.major_head, leafs, stats);
        if (res) {
            ReplaceBuilding(p.major_head, res.value());
        }
    }

    void ImproveMinorHead(int idx) {
        auto& leafs = pattern.data[idx] == 0 ? bc.MinorHeadLeafs() : bc.leafs(pattern.data[idx]);
        auto res = ImproveBuilding(p.data[idx], leafs, stats);
        if (res) {
            ReplaceBuilding(p.data[idx], res.value());
        }
    }

    void ImprovePort(int idx) {
        auto& leafs = pattern.data[idx] == 0 ? bc.PortLeafs() : bc.leafs(pattern.data[idx]);
        auto res = ImproveBuilding(p.data[idx], leafs, stats);
        if (res) {
            ReplaceBuilding(p.data[idx], res.value());
        }
    }

    void ImproveMajorOther(int idx) {
        auto& leafs = pattern.data[idx] == 0 ? bc.MajorOtherLeafs() : bc.leafs(pattern.data[idx]);
        auto res = ImproveBuilding(p.data[idx], leafs, p.major_other(), stats);
        if (res) {
            ReplaceBuilding(p.data[idx], res.value());
        }
    }

    void ImproveMinorOther(int idx) {
        int idx_another = idx + 1;
        if ((idx - p.start_minor_other) % 2 == 1) {
            idx_another = idx - 1;
        }
        auto& leafs = pattern.data[idx] == 0 ? bc.MinorOtherLeafs() : bc.leafs(pattern.data[idx]);
        auto res = ImproveBuilding(p.data[idx], leafs, std::span<int>(p.data).subspan(idx_another, 1), stats);
        if (res) {
            ReplaceBuilding(p.data[idx], res.value());
        }
    }

    void Solve() {
        try {
            std::vector<std::function<void()>> improve_set;
            improve_set.push_back([&]() { ImproveMajorHead(); });
            for (auto i = 0; i < p.start_ports; ++i) {
                improve_set.push_back([&, i]() { ImproveMinorHead(i); });
            }
            for (auto i = p.start_ports; i < p.start_major_other; ++i) {
                improve_set.push_back([&, i]() { ImprovePort(i); });
            }
            for (auto i = p.start_major_other; i < p.start_minor_other; ++i) {
                improve_set.push_back([&, i]() { ImproveMajorOther(i); });
            }
            for (auto i = p.start_minor_other; i < p.data.size(); ++i) {
                improve_set.push_back([&, i]() { ImproveMinorOther(i); });
            }

            unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
            std::default_random_engine rng(seed);
            for (;;) {
                double current_score = score(stats);
                std::shuffle(improve_set.begin(), improve_set.end(), rng);
                for (auto &func: improve_set) {
                    func();
                }
                double new_score = score(stats);
                if (new_score - current_score < 1e-6) {
                    // no improvement done.
                    break;
                }
            }
        } catch (std::exception& e) {
            auto fmt = boost::format("LocalSearch::Solve");
            std::throw_with_nested(std::runtime_error(fmt.str()));
        }
    }
};
