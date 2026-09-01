#include <iostream>
#include <format>
#include <numeric>
#include "pack_parser/pack_parser.hpp"
#include "save_parser/parser.hpp"


std::vector<File> parse_pack(std::istream& in) {
    // Check if it has the weird steam-only header, and skip it if found.
    const std::string MFH_PREAMBLE = "MFH";
    std::vector<char> buffer(MFH_PREAMBLE.size());
    in.read(buffer.data(), MFH_PREAMBLE.size());
    size_t start = 0;
    if (buffer == std::vector<char>(MFH_PREAMBLE.begin(), MFH_PREAMBLE.end())) {
        start = 8;
    }
    in.seekg(-MFH_PREAMBLE.size(), std::ios::cur);
    in.seekg(start, std::ios::cur);


    std::vector<char> pfh_version_buffer(4);
    in.read(pfh_version_buffer.data(), 4);
    std::string pfh_version(pfh_version_buffer.begin(), pfh_version_buffer.end());

    /// PFH6: Used in Troy (v1.3.0+).
    /// PFH5: Used in Warhammer 2, Warhammer 3, Three Kingdoms, Troy (pre-1.3.0), Pharaoh, Pharaoh Dynasties, Arena.
    /// PFH4: Used in Warhammer 1, Attila, Rome 2, Thrones of Britannia.
    /// PFH3: Used in Shogun 2.
    /// PFH2: Used in Shogun 2 before patch 15 (Fall of the Samurai expansion).
    /// PFH0: Used in Napoleon and Empire.
    if (pfh_version != "PFH4") {
        throw std::runtime_error(std::format("PFH version {} found", pfh_version));
    }

    auto pack_type = read<uint32_t>(in);
    std::cout << pack_type << std::endl;

    auto packs_count = read<uint32_t>(in);
    auto packs_index_size = read<uint32_t>(in);

    auto files_count = read<uint32_t>(in);
    auto files_index_size = read<uint32_t>(in);

    std::cout << packs_count << " " << packs_index_size << " " << files_count << " " << files_index_size << std::endl;

    auto ts = read<uint32_t>(in);

    // auto indexes_size = 0 + packs_index_size + files_index_size;
    // std::vector<char> buffer_data(indexes_size);
    // in.read(buffer_data.data(), indexes_size);
    //
    // auto count = std::count(buffer_data.begin(), buffer_data.end(), 0);
    //
    // std::cout << std::string(buffer_data.begin(), buffer_data.end()) << std::endl;
    //
    // std::cout << "count " << count << std::endl;

    std::vector<File> files(files_count);
    for (auto& fi : files) {
        fi.size = read<uint32_t>(in);
        std::string path;
        std::getline(in, path, '\0');
        std::replace(path.begin(), path.end(), '\\', '/');
        fi.path = path;

        std::cout << fi.path << " " << fi.size << std::endl;
    }

    size_t total_file_size = std::accumulate(files.begin(), files.end(), 0, [](uint32_t sz, auto& file) {
        return sz + file.size;
    });
    std::cout << total_file_size << std::endl;


    for (auto& fi : files) {
        fi.start_pos = in.tellg();
        in.seekg(fi.size, std::ios::cur);
    }
    return files;
}