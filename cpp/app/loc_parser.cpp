#include <fstream>
#include <iostream>
#include <filesystem>
#include <algorithm>
#include <boost/program_options.hpp>
#include <boost/locale.hpp>
#include "loc_parser/loc_parser.hpp"


namespace po = boost::program_options;


int main(int ac, const char *av[]) {
    std::string loc_file_path_str{};
    po::variables_map vm;

    try {
        po::options_description desc{"Options"};
        desc.add_options()
                ("loc-file-path", po::value<std::string>(&loc_file_path_str)->required(), "Game loc file path");
        store(parse_command_line(ac, av, desc), vm);
        notify(vm);
    }
    catch (const po::error &ex)
    {
        std::cerr << ex.what() << '\n';
    }

    std::filesystem::path loc_file_path(loc_file_path_str);
    std::ifstream file(loc_file_path, std::ios::binary);
    auto entries = parse_loc(file);

    for (auto i = 0; i < std::min(static_cast<size_t>(20), entries.size()); ++i) {
        auto key = boost::locale::conv::utf_to_utf<char>(entries[i].key);
        auto value = boost::locale::conv::utf_to_utf<char>(entries[i].value);
        std::cout << key << " " << value << std::endl;
    }

    // should output to file or something.
}