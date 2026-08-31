#pragma once
#include <string>
#include <vector>
#include <iostream>
#include <boost/program_options.hpp>
#include <boost/log/core.hpp>
#include "building_collection.hpp"
#include "building_util.hpp"
#include "stats_util.hpp"
#include "province_str.hpp"
#include "province_stats.hpp"
#include "province_candidates.hpp"
#include "score.hpp"
#include "local_search.hpp"
#include "rank_building_collection.hpp"
#include "province_str.hpp"
#include "province_out.hpp"
#include "profile.hpp"
#include "bonus_stats.hpp"

namespace cli {

namespace po = boost::program_options;

struct Args {
    int argc;
    const char** argv;
};

class Global {
    Args args_;
    po::options_description options_{"Options"};
    po::positional_options_description pos_options_;

    std::string config_filename;
    std::string buildings_filename;
    std::string profile_filename;
    std::vector<std::string> no_resource;
    std::string command_;
    std::vector<Building> buildings_;
    Profile profile_;

public:
    bool Handle(Args args) {
        args_ = args;

        options_.add_options()
                ("help,h", "produce help message")
                ("trace,t", "trace computation")
                ("config", po::value<std::string>(&config_filename), "yaml filename with paths to all other paths")
                ("buildings-filename", po::value<std::string>(&buildings_filename), "yaml filename where buildings are stored")
                ("no-resource", po::value<std::vector<std::string>>(&no_resource), "list of resources that are not available")
                ("command", po::value<std::string>()->required(), "command to execute: find-leafs");

        auto sub_desc = options_;
        sub_desc.add_options()("other args", po::value<std::vector<std::string>>(), "other args");

        pos_options_.add("command", 1);
        auto sub_pos_desc = pos_options_;
        sub_pos_desc.add("other args", -1);

        po::variables_map vm;
        auto parsed_options = po::command_line_parser(args.argc, args.argv).
                options(sub_desc).
                positional(sub_pos_desc).
                allow_unregistered().
                run();
        po::store(parsed_options, vm);

        if (vm.count("help")) {
            std::cout << options_ << std::endl;
            std::cout << "Can pass <buildings> as a single positional argument." << std::endl;
            return true;
        }

        // sets buildings_filename variable, will throw if not set
        po::notify(vm);

        boost::log::core::get()->set_logging_enabled(false);
        if (vm.count("trace")) {
            boost::log::core::get()->set_logging_enabled(true);
        }

        if (!config_filename.empty()) {
            auto node = YAML::LoadFile(config_filename);
            buildings_filename = node["BuildingsPath"].Scalar();
            profile_filename = node["ProfilePath"].Scalar();
        }

        // make empty building at zero
        buildings_ = read_buildings(buildings_filename);
        buildings_.insert(buildings_.begin(), Building{});
        std::cout << "Buildings read: " << buildings_.size() << std::endl;

        std::erase_if(buildings_, [&](const auto& b) {
            return b.need_resource && std::count(no_resource.begin(), no_resource.end(), b.need_resource.value()) > 0;
        });
        if (!no_resource.empty()) {
            std::cout << "No resource pruned to: " << buildings_.size() << std::endl;
        }

        if (!profile_filename.empty()) {
            profile_ = read_profile(profile_filename);
        }

        command_ = vm["command"].as<std::string>();
        return false;
    }

    po::variables_map Notify() {
        po::variables_map vm;
        auto parsed_options = po::command_line_parser(args_.argc, args_.argv).
                options(options_).
                positional(pos_options_).
                run();
        po::store(parsed_options, vm);

        // sets variables, will throw if not set
        po::notify(vm);
        return vm;
    }

    [[nodiscard]] const std::string& command_name() const {
        return command_;
    }

    [[nodiscard]] auto& options() {
        return options_;
    }

    [[nodiscard]] auto& pos_options() {
        return pos_options_;
    }

    [[nodiscard]] auto args() const {
        return args_;
    }

    [[nodiscard]] const auto& buildings() const {
        return buildings_;
    }

    [[nodiscard]] const auto& profile() const {
        return profile_;
    }
};

class Cmd {
public:
    [[nodiscard]] virtual const char* name() const = 0;
    virtual void Handle(Global& global) = 0;
    virtual ~Cmd() = default;
};


class FindLeafsCmd : public Cmd {
    [[nodiscard]] const char* name() const override {
        return "find-leafs";
    }

    void Handle(Global& global) override {
        std::string building_name;
        global.options().add_options()("building", po::value<std::string>(&building_name)->required());
        global.pos_options().add("building", 1);
        global.Notify();

        auto leafs = BuildingCollection(global.buildings()).find_leafs(building_name);
        for (const auto &name: leafs) {
            std::cout << name << std::endl;
        }
    }
};

class ResourceLeafsCmd : public Cmd {
    [[nodiscard]] const char* name() const override {
        return "resource-leafs";
    }

    void Handle(Global& global) override {
        BuildingCollection bc(global.buildings());
        for (auto i: bc.Leafs()) {
            if (!bc[i].need_resource) {
                continue;
            }
            ant::Println(std::cout, bc[i].name, " - ", bc[i].need_resource.value());
        }
    }
};

class ResourceBuildingsCmd : public Cmd {
    [[nodiscard]] const char* name() const override {
        return "resource-buildings";
    }

    void Handle(Global& global) override {
        for (const auto &b: global.buildings()) {
            if (!b.need_resource) {
                continue;
            }
            ant::Println(std::cout, b.name, " - ", b.need_resource.value());
        }
    }
};

class MajorOnlyLeafsCmd : public Cmd {
    [[nodiscard]] const char* name() const override {
        return "major-only-leafs";
    }

    void Handle(Global& global) override {
        BuildingCollection bc(global.buildings());
        for (auto i: bc.MajorOnlyOtherLeafs()) {
            PrintRegion(std::array{i}, bc);
        }
    }
};

class CommonLeafsCmd : public Cmd {
    [[nodiscard]] const char* name() const override {
        return "common-leafs";
    }

    void Handle(Global& global) override {
        BuildingCollection bc(global.buildings());
        for (auto i: bc.CommonOtherLeafs()) {
            PrintRegion(std::array{i}, bc);
        }
    }
};


class SolveCmd : public Cmd {
    [[nodiscard]] const char* name() const override {
        return "solve";
    }

    void Handle(Global& global) override {
        std::string province_str;
        global.options().add_options()("province", po::value<std::string>(&province_str)->required());
        global.pos_options().add("province", 1);

        global.Notify();

        auto regions_str = Split(province_str, '|');
        auto bc = BuildingCollection(global.buildings());
        ant::Println(std::cout, "Created BuildingCollection");
        // maybe should do switch a little later
        switch (regions_str.size()) {
            case 2:
                Solve<2>(regions_str, bc);
                break;
            case 3:
                Solve<3>(regions_str, bc);
                break;
            case 4:
                Solve<4>(regions_str, bc);
                break;
            default:
                auto msg = boost::format("region count %1% is unexpected") % regions_str.size();
                throw std::invalid_argument("region");
        }
    }

    template <int region_count>
    static void Solve(const std::vector<std::string>& regions_str, const BuildingCollection& bc) {
        std::array<std::vector<std::string>, region_count> regions_building_names;
        for (auto i = 0; i < region_count; ++i) {
            regions_building_names[i] = regions_str[i] == "" ?
                                        std::vector<std::string>{} : Split(regions_str[i], ',');
        }
        Province<region_count> province = ParseProvince<region_count>(bc, regions_building_names);
        PrintProvince(province, bc);
    }
};

class CountCmd : public Cmd {
    [[nodiscard]] const char* name() const override {
        return "count";
    }

    void Handle(Global& global) override {
        // counts number of unique building placements
        global.options().add_options()
                ("port,p", "province major has a port");
        global.options().add_options()
                ("port2,p2", "province minor has a port");

        auto vm = global.Notify();

        auto bc = BuildingCollection(global.buildings());
        bool has_port = vm.count("port");
        bool has_port_2 = vm.count("port2");
        ant::Println(std::cout, "EmptyCapitalCandidates:", CountEmptyCapitalCandidates(bc, has_port));
        ant::Println(std::cout, "EmptyCapitalWithOneMinorCandidates:", CountEmptyMajorWithOneMinorCandidates(bc, has_port, has_port_2));
    }
};

class CombCmd : public Cmd {
    [[nodiscard]] const char* name() const override {
        return "comb";
    }

    void Handle(Global& global) override {
        int select_count, elem_count;
        global.options().add_options()
                ("select_count", po::value<int>(&select_count)->required())
                ("elem_count", po::value<int>(&elem_count)->required());
        global.pos_options()
            .add("select_count", 1)
            .add("elem_count", 1);

        global.Notify();
        ant::Println(std::cout, "Combinations:", CombinationsCount(select_count, elem_count));
    }
};

class GA_Cmd : public Cmd {
    [[nodiscard]] const char* name() const override {
        return "ga";
    }

    void Handle(Global& global) override {
        auto bc = BuildingCollection(global.buildings());
        auto population = ga::MakePopulation(bc, 2, 2, 10);
        for (const auto &p : population) {
            PrintRegion(p, bc);
            std::cout << "end" << std::endl;
        }
    }
};

class RandomCmd : public Cmd {
    [[nodiscard]] const char* name() const override {
        return "random";
    }

    void Handle(Global& global) override {
        auto bc = BuildingCollection(global.buildings());
        auto p = RandomProvince(bc, 2, 2);
        Print(p, bc);
    }
};

class LocalSearchCmd : public Cmd {
    [[nodiscard]] const char* name() const override {
        return "local-search";
    }

    void Handle(Global& global) override {
        std::string profile_province_id;
        std::string province_str;
        int iterations;
        int min_order;
        int min_food;
        BonusStats bonus_stats;
        int rank;
        bool init_random = false;
        global.options().add_options()
                ("profile", po::value<std::string>(&profile_province_id), "profile province name or alias")
                ("province", po::value<std::string>(&province_str))
                ("init-random", po::bool_switch(&init_random))
                ("iter", po::value<int>(&iterations)->default_value(1))
                ("order", po::value(&min_order)->default_value(0))
                ("food", po::value(&min_food)->default_value(0))
                ("rank", po::value(&rank)->default_value(10))
                ("bonus-industry", po::value(&bonus_stats.wealth_pct_industry)->default_value(0));
        global.pos_options().add("province", 1);

        global.Notify();

        if (!profile_province_id.empty()) {
            province_str = global.profile()[profile_province_id].province_str;
        }
        auto pr = SplitProvinceStr(province_str);
        auto bc = BuildingCollection(global.buildings());
        auto rank_bc = RankBuildingCollection(bc, rank);
        auto pr_v = ParseProvince(bc, pr);
        auto pattern = ConvertToVectorSliced(pr_v);
        Score score(Constraints{min_food, min_order, 1000, 1000});

        ant::Println(std::cout, "Pattern:");
        Print(pattern, bc);
        PrintStats(TotalStats(pattern, bc.buildings()) + bonus_stats);

        ProvinceVectorSliced best_solution;
        double best_score = 0;
        for (auto i = 0; i < iterations; ++i) {
            auto p = init_random ? RandomProvinceWithPattern(rank_bc, pattern) : pattern;

//            auto best_pr_v = ConvertToProvinceV(p, pr_v);
//            std::cout << ProvinceStr(best_pr_v, bc) << std::endl;

            LocalSearch local_search(p, pattern, rank_bc, score, bonus_stats);
            local_search.Solve();

            double new_score = score(TotalStats(p, bc.buildings()) + bonus_stats);
            if (new_score - best_score > 1e-6) {
                best_solution = p;
                best_score = new_score;
                ant::Println(std::cout, "iter: ", i, " score: ", best_score);
            }
        }

        ant::Println(std::cout, "Local Search Solution:");
        // could be no solution and this thing is not possible. be prepared
        auto best_pr_v = ConvertToProvinceV(best_solution, pr_v);
        std::cout << ProvinceStr(best_pr_v, bc) << std::endl;
        Print(best_solution, bc);
        PrintStats(TotalStats(best_solution, bc.buildings()) + bonus_stats);
        ant::Println(std::cout, score(TotalStats(best_solution, bc.buildings()) + bonus_stats));
    }
};

class StatsCmd : public Cmd {
    [[nodiscard]] const char* name() const override {
        return "stats";
    }

    void Handle(Global& global) override {
        std::string province_str;
        global.options().add_options()
                ("province", po::value<std::string>(&province_str)->required());
        global.pos_options().add("province", 1);

        global.Notify();

        auto pr = SplitProvinceStr(province_str);
        auto bc = BuildingCollection(global.buildings());
        auto pr_v = ParseProvince(bc, pr);
        auto pr_vc = ConvertToVectorSliced(pr_v);
        auto stats = TotalStats(pr_vc, bc.buildings());
        auto node = stats_to_node(stats);
        YAML::Emitter emitter;
        emitter << node;
        std::cout << "Stats: " << std::endl;
        PrintStats(stats);
        std::cout << emitter.c_str() << std::endl;
    }
};

}