#pragma once
#include <fstream>
#include <filesystem>
#include <jsoncpp/json/json.h>


struct File {
    std::size_t size;
    std::filesystem::path path;
    std::streampos start_pos;
};


std::vector<File> parse_pack(std::istream& in);