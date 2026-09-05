#include <fstream>
#include <iostream>
#include <filesystem>
#include <span>
#include <boost/program_options.hpp>
#include <ant/core/core.hpp>
#include "save_parser/parser.hpp"
#include "save_parser/esf_parser.hpp"
#include "save_parser/provinces.hpp"
#include "save_parser/factions.hpp"


namespace po = boost::program_options;


const Json::Value* go_to(const Json::Value& obj, const std::span<std::string>& path) {
    if (path.empty()) {
        return &obj;
    }
    if (path.front() == "[]") {
        for (auto& item: obj) {
            auto res = go_to(item, path.subspan(1));
            if (res != nullptr) {
                return res;
            }
        }

        for (auto& item: obj) {
            if (item.isObject() && item.isMember("Name")) {
                std::cout << "next arr: " << item["Name"] << '\n';
            }
        }

        return nullptr;
    }
    if (obj.isObject() && obj.isMember("Name") && obj["Name"] == path.front()) {
        return go_to(obj["Nodes"], path.subspan(1));
    }
    return nullptr;
}

void extract_regions(const std::filesystem::path& save_file_path, const Json::Value& obj) {
    auto regions_json_path = "CAMPAIGN_SAVE_GAME/[]/CAMPAIGN_SAVE_GAME/[]/"
                                         "CAMPAIGN_ENV/[]/CAMPAIGN_MODEL/[]/WORLD/[]/"
                                         "REGION_MANAGER/[]/REGIONS_ARRAY";
    auto path_items = ant::Split(regions_json_path, '/');

    auto regions = go_to(obj, path_items);
    if (regions != nullptr) {
        auto regions_directory_path = save_file_path.parent_path();
        regions_directory_path /= "regions";
        std::filesystem::create_directory(regions_directory_path);

        for (auto& region: (*regions)) {
            auto region_name = region[0]["Nodes"][1].asString();
            if (region_name.size() > 100) {
                throw std::runtime_error("something is wrong");
            }
            auto regions_filename = save_file_path.filename();
            regions_filename.replace_extension();
            regions_filename += "-regions-" + region_name;
            regions_filename = regions_directory_path / regions_filename;
            std::ofstream out(regions_filename);
            Json::StyledStreamWriter().write(out, region);
        }
    }
}


std::vector<const Json::Value*> get_faction_objs(const Json::Value& obj) {
    auto factions_json_path = "CAMPAIGN_SAVE_GAME/[]/CAMPAIGN_SAVE_GAME/[]/"
                                          "CAMPAIGN_ENV/[]/CAMPAIGN_MODEL/[]/WORLD/[]/"
                                          "FACTION_ARRAY";
    auto path_items = ant::Split(factions_json_path, '/');
    auto factions = go_to(obj, path_items);
    if (factions == nullptr) {
        return {};
    }
    std::vector<const Json::Value*> res;
    for (auto& faction: (*factions)) {
        auto nodes = faction[0]["Nodes"];
        res.push_back(&nodes);
    }
    return res;
}


Factions get_factions(const Json::Value& obj) {
    auto faction_objs = get_faction_objs(obj);
    std::vector<Faction> fns;
    for (auto& obj: faction_objs) {
        auto fn = Faction{.idx=(*obj)[0].asUInt64(),
                          .id=(*obj)[2]["Nodes"][1].asString()};
        fns.push_back(fn);
    }
    return {fns};
}


std::string get_user_faction_id(const Json::Value& obj) {
    auto provinces_json_path = "CAMPAIGN_SAVE_GAME/[]/SAVE_GAME_HEADER";
    auto path_items = ant::Split(provinces_json_path, '/');
    auto header_obj = go_to(obj, path_items);
    if (header_obj != nullptr) {
        return (*header_obj)[0].asString();
    }
    throw std::runtime_error("User faction id not found.");
}


struct Region {

};



Json::Value get_faction_regions_obj() {
    return {};
}


void extract_factions(const std::filesystem::path& save_file_path, const Json::Value& obj) {
    auto factions_json_path = "CAMPAIGN_SAVE_GAME/[]/CAMPAIGN_SAVE_GAME/[]/"
                                          "CAMPAIGN_ENV/[]/CAMPAIGN_MODEL/[]/WORLD/[]/"
                                          "FACTION_ARRAY";
    auto path_items = ant::Split(factions_json_path, '/');

    auto factions = go_to(obj, path_items);
    if (factions != nullptr) {
        auto factions_directory = save_file_path.parent_path();
        factions_directory /= "factions";
        std::filesystem::create_directories(factions_directory);

        for (auto& faction: (*factions)) {
            auto faction_name = faction[0]["Nodes"][0].asString();

            auto filename = save_file_path.filename();
            filename.replace_extension();
            filename = filename.string() + "-factions-" + faction_name + ".json";
            auto factions_file_path = factions_directory / filename;
            factions_file_path.replace_extension("json");
            std::ofstream out(factions_file_path);
            Json::StyledStreamWriter().write(out, faction);
        }
    }
}

void extract_provinces(const std::filesystem::path& save_file_path, const Json::Value& obj) {
    auto provinces_json_path = "CAMPAIGN_SAVE_GAME/[]/CAMPAIGN_SAVE_GAME/[]/"
                              "CAMPAIGN_ENV/[]/CAMPAIGN_MODEL/[]/CAMPAIGN_MAP_DATA/[]/"
                              "PROVINCES_DATA/[]/PROVINCE_DATA_ARRAY";
    auto path_items = ant::Split(provinces_json_path, '/');
    auto provinces_obj = go_to(obj, path_items);
    Provinces provinces;
    if (provinces_obj != nullptr) {
        for (auto& province_obj: (*provinces_obj)) {
            auto& nodes = province_obj[0]["Nodes"];
            Province province;
            province.id = nodes[0].asString();
            province.capital_region_id = nodes[2].asString();
            for (auto& item: nodes[1]["Nodes"]) {
                province.region_ids.push_back(item[0].asString());
            }
            provinces.AddProvince(province);
        }
        auto provinces_file_path = save_file_path;
        provinces_file_path.replace_extension();
        provinces_file_path.replace_filename(provinces_file_path.filename().string() + "-provinces");
        provinces_file_path.replace_extension("json");
        std::ofstream out(provinces_file_path);
        Json::StyledStreamWriter().write(out, provinces.to_json());
    }
}





/*
 * Want something like
 * province_id.
 *  region_id.
 *    buildings.
 */
//void extract_user_regions() {
//
//}

int main(int ac, const char *av[]) {
    std::string save_file_path_str{};
    po::variables_map vm;

    try {
        po::options_description desc{"Options"};
        desc.add_options()
                ("save-file-path", po::value<std::string>(&save_file_path_str)->required(), "Game save file path")
                ("extract-regions", "Extract regions into a separate directory one per file. "
                                    "Easier to read and compare json data.")
                ("extract-factions", "Extract factions into a separate directory one per file. "
                                     "Easier to read and compare json data.")
                ("extract-provinces", "Extract and format provinces into a separate file.");
        store(parse_command_line(ac, av, desc), vm);
        notify(vm);
    }
    catch (const po::error &ex)
    {
        std::cerr << ex.what() << '\n';
    }

    std::filesystem::path save_file_path(save_file_path_str);
    auto json_file_path = save_file_path;
    json_file_path.replace_extension("json");

    // tmp/my_auto_save_legendary.json
    std::ifstream file(save_file_path, std::ios::binary);
    auto json_obj = parse_esf(file);
    std::ofstream out(json_file_path);
    Json::StyledStreamWriter().write(out, json_obj);

    auto user_faction_id = get_user_faction_id(json_obj);
    std::cout << user_faction_id << "\n";

    if (vm.count("extract-regions")) {
        extract_regions(save_file_path, json_obj);
    }
    if (vm.count("extract-factions")) {
        extract_factions(save_file_path, json_obj);
    }
    if (vm.count("extract-provinces")) {
        extract_provinces(save_file_path, json_obj);
    }
    // want to recognise user faction and then look at user regions.
    // the output:
    // array of regions,
    // each region:
    //  array of buildings
    //  region name - could also include province name


    // extract provinces:
    // make a data structure:
    // unordered_map: region_id -<
}