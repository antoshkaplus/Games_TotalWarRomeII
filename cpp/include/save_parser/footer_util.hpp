#pragma once
#include <fstream>
#include <vector>
#include "parser.hpp"


inline std::vector<std::string> read_footer_ansii_strings(std::istream& in) {
    auto count = read<uint32_t>(in);
    std::vector<std::string> res(count);
    std::vector<char> buffer;
    for (auto i = 0; i < count; ++i) {
        auto len = read<uint16_t>(in);
        buffer.resize(len);
        in.read(buffer.data(), len);
        std::string value(buffer.data(), len);
        auto key = read<uint32_t>(in);
        res[key] = value;
    }
    return res;
}

inline std::vector<std::u16string> read_footer_utf16_strings(std::istream& in) {
    auto count = read<uint32_t>(in);
    std::vector<std::u16string> res(count);
    std::vector<char16_t> buffer;
    for (auto i = 0; i < count; ++i) {
        auto len = read<uint16_t>(in);
        buffer.resize(sizeof(char16_t) * len);
        in.read(reinterpret_cast<char *>(buffer.data()), sizeof(char16_t) * len);
        std::u16string value(buffer.data(), len);
        auto key = read<uint32_t>(in);
        res[key] = value;
    }
    return res;
}

inline std::vector<std::string> transform_utf16_to_char_strings(std::vector<std::u16string>& utf16_strings, char utf16_placeholder) {
    std::vector<std::string> res(utf16_strings.size());
    std::vector<char> buffer;
    for (auto& p: utf16_strings) {
        buffer.resize(p.size());
        std::transform(p.begin(),
                       p.end(),
                       buffer.begin(),
                       [=](char16_t ch16) {
                           return ch16 == static_cast<char8_t>(ch16)
                                  ? static_cast<char>(ch16) : utf16_placeholder;
                       });
        res.emplace_back(buffer.data(), buffer.size());
    }
    return res;
}

Json::Value strings_to_json(const std::vector<std::string>& ss) {
    Json::Value obj;
    for (auto i = 0; i < ss.size(); ++i) {
        obj[std::to_string(i)] = ss[i];
    }
    return obj;
}