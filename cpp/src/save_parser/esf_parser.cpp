#include "save_parser/esf_parser.hpp"
#include "save_parser/file_type.hpp"
#include "save_parser/parser.hpp"
#include "save_parser/abca_parser.hpp"
#include "save_parser/footer_util.hpp"


Json::Value parse_esf(std::istream& in) {
    FileType file_type;
    in.read(reinterpret_cast<char*>(&file_type), sizeof(FileType));
    std::cout << file_type << "\n";

    if (file_type != FileType::ABCD) {
        const int skip_bytes = 8;
        in.seekg(skip_bytes, std::ios_base::cur);
    }
    auto footer_offset = read<uint32_t>(in);
    std::cout << "Footer offset: " << footer_offset << "\n";

    auto body_start_pos = in.tellg();
    in.seekg(footer_offset, std::ios_base::beg);
    auto node_names = parse_node_names(in);
    for (const auto& name: node_names) {
        std::cout << name << "\n";
    }

    switch (file_type) {
        case FileType::ABCA: {
            auto utf16_strings = read_footer_utf16_strings(in);
            auto utf16_strings_like_ansii = transform_utf16_to_char_strings(utf16_strings, '?');
            auto ansii_strings = read_footer_ansii_strings(in);
            auto params = abca::Params{node_names, ansii_strings, utf16_strings_like_ansii};
            in.seekg(body_start_pos);
            return abca::parse(in, params);
        }
        case FileType::ABCF: {
            auto utf16_strings = read_footer_utf16_strings(in);
            auto ansii_strings = read_footer_ansii_strings(in);
        }
        default:
        {
            throw std::runtime_error("FileType not implemented");
        }
    }
}