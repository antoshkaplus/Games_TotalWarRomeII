#include <istream>
#include <format>
#include "loc_parser/loc_parser.hpp"
#include "save_parser/parser.hpp"


std::u16string read_u16str(std::istream& in) {
    auto sz = read<uint16_t>(in);
    std::u16string res(sz, '\0');
    in.read(reinterpret_cast<char*>(res.data()), sizeof(char16_t) * sz);
    return res;
}


std::vector<Entry> parse_loc(std::istream& in) {
    // Read header. It is always \FF\FE => 0xFEFF
    auto file_mark = read<uint16_t>(in);
    if (file_mark != 0xFEFF) {
        throw std::runtime_error("Unexpected file format");
    }
    std::string file_format;
    std::getline(in, file_format, '\0');
    if (file_format != "LOC") {
        throw std::runtime_error("Unexpected file format");
    }
    auto version = read<int32_t>(in);
    if (version != 1) {
        throw std::runtime_error(std::format("Unexpected file version {}", version));
    }
    auto entry_count = read<uint32_t>(in);
    std::vector<Entry> entries(entry_count);
    for (auto& e : entries) {
        e.key = read_u16str(in);
        e.value = read_u16str(in);
        read<char>(in);
    }
    return entries;
}