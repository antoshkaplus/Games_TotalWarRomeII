#pragma once
#include <fstream>
#include <iostream>
#include <vector>
#include <boost/format.hpp>
#include <jsoncpp/json/json.h>
#include "save_parser/file_type.hpp"
//#include "save_parser/node_type.hpp"


struct NodeType {
    uint8_t value{};

    bool COORD_2D() const {
        return value == 0x0c;
    }
    bool COORD_3D() const {
        return value == 0x0d;
    }
    bool INT8() const {
        return value == 0x02;
    }
    bool INT16() const {
        return value == 0x03;
    }
    bool INT32() const {
        return value == 0x04;
    }
    bool FLOAT() const {
        return value == 0x0a;
    }
    bool ASCII() const {
        return value == 0x0f;
    };
    bool UTF16() const {
        return value == 0x0e;
    }
    bool FLOAT_ARRAY() const {
        return value == 0x4a;
    }
    bool UINT32_ARRAY() const {
        return value == 0x48;
    }
    bool UINT16_ARRAY() const {
        return value == 0x47;
    }
    bool UINT8_ARRAY() const {
        return value == 0x46;
    }
    bool INT8_ARRAY() const {
        return value == 0x42;
    }
    bool BOOL_ARRAY() const {
        return value == 0x41;
    }
    bool UINT8() const {
        return value == 0x06;
    }
    bool UINT16() const {
        return value == 0x07;
    }
    bool UINT32() const {
        return value == 0x08;
    }
    bool UINT64() const {
        return value == 0x09;
    }
    bool UINT64_ARRAY() const {
        return value == 0x49;
    }
    bool ANGLE() const {
        return value == 0x10;
    }
};

inline std::ostream& operator<<(std::ostream& out, NodeType node_type) {
    if (node_type.ASCII()) {
        out << "ASCII";
    } else {
        throw std::runtime_error("Unexpected NodeType value.");
    }
    return out;
}

template<class Value>
Value read(std::istream& in) {
    Value val;
    in.read(reinterpret_cast<char*>(&val), sizeof(val));
    return val;
}

inline std::string read_str(std::istream& in) {
    auto str_len = read<uint16_t>(in);
    constexpr uint16_t MAX_STR_LENGTH = 256;
    char buff[MAX_STR_LENGTH];
    if (str_len > MAX_STR_LENGTH) {
        throw std::runtime_error("Unsupported string length.");
    }
    in.read(buff, str_len);
    return {buff, str_len};
}

inline uint32_t read_uintvar(std::istream& in) {
    auto byte = read<uint8_t>(in);
    uint64_t result = 0;
    while(byte & 0x80)
    {
        result = (result << 7) | (byte & 0x7f); // 0b0111'1111
        byte = read<uint8_t>(in);
    }
    result = (result << 7) + (byte & 0x7f);
    return result;
}

inline std::vector<std::string> parse_node_names(std::istream& in) {
    auto num = read<uint16_t>(in);
    std::vector<std::string> res(num);
    for (int i = 0; i < num; i++) {
        res[i] = read_str(in);
    }
    return res;
}

// for now just print whatever you find, later will save to YAML::Node
inline Json::Value parse_node(std::istream& in, NodeType node_type) {
    Json::Value res;
    if (node_type.UINT32()) {
        auto numb = read<uint32_t>(in);
        res = numb;
    } else if (node_type.UINT16()) {
        res = read<uint16_t>(in);
    } else if (node_type.UINT8()) {
        res = read<uint8_t>(in);
    } else if (node_type.ANGLE()) {
        res = read<uint16_t>(in);
    } else if (node_type.INT8()) {
        res = read<int8_t>(in);
    } else if (node_type.INT16()) {
        res = read<int16_t>(in);
    } else if (node_type.INT32()) {
        res = read<int32_t>(in);
    } else if (node_type.UINT64()) {
        res = read<int64_t>(in);
    } else if (node_type.FLOAT()) {
        res = read<float>(in);
    } else if (node_type.ASCII()) {
        auto s = read_str(in);
        throw std::runtime_error("Unexpected");
    } else if (node_type.COORD_2D()) {
        read<std::array<float, 2>>(in);
    } else if (node_type.COORD_3D()) {
        read<std::array<float, 3>>(in);
    } else if (node_type.UINT32_ARRAY()) {
        throw std::runtime_error("Unexpected");
    } else if (node_type.UINT16_ARRAY()) {
        throw std::runtime_error("Unexpected");
    } else {
        auto fmt = boost::format("Unexpected Node Type: %1$#x.") % static_cast<uint32_t>(node_type.value);
        throw std::runtime_error(fmt.str());
    }
    return res;
}
