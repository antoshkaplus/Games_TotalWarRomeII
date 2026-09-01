#include <fstream>
#include <iostream>
#include <filesystem>
#include <boost/program_options.hpp>
#include "pack_parser/pack_parser.hpp"


namespace po = boost::program_options;


int main(int ac, const char *av[]) {
    std::string pack_file_path_str{};
    po::variables_map vm;

    try {
        po::options_description desc{"Options"};
        desc.add_options()
                ("pack-file-path", po::value<std::string>(&pack_file_path_str)->required(), "Game pack file path");
        store(parse_command_line(ac, av, desc), vm);
        notify(vm);
    }
    catch (const po::error &ex)
    {
        std::cerr << ex.what() << '\n';
    }

    std::filesystem::path pack_file_path(pack_file_path_str);
    std::ifstream file(pack_file_path, std::ios::binary);
    auto pack_files = parse_pack(file);

    std::vector<char> buffer;
    std::filesystem::path prefix = pack_file_path.replace_extension();
    for (auto& fi: pack_files) {
        buffer.resize(fi.size);
        file.seekg(fi.start_pos);
        file.read(buffer.data(), fi.size);

        std::filesystem::path path = prefix / fi.path;
        std::cout << path.string() << '\n';

        std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path, std::ios::binary);
        if (!out) {
            throw std::runtime_error("Failed to open game pack file " + path.string());
        }
        out.write(buffer.data(), fi.size);
    }
}