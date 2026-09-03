#pragma once
#include <jsoncpp/json/json.h>
#include <lzma.h>
#include <algorithm>
#include <sstream>
#include "parser.hpp"
#include "byte_array.hpp"
#include "esf_parser.hpp"
#include "json_util.hpp"

namespace abca {

struct Params {
    std::vector<std::string> node_names;
    std::vector<std::string> ansii_strings;
    std::vector<std::string> utf16_strings;
};

struct NodeType: ::NodeType {
    bool RootRecord() const {
        return value == 0x80; // 0b1000'0000
    }
    bool Record() const {
        return value == 0xa0; // 0b1010'0000
    }
    bool Record_OptInfo() const {
        return value >= 0x80 && value <= 0x9f; // 0b1000'0000 - 0b1001'1111
    }
    bool RecordsArray() const {
        return value == 0xe0; // 0b1110'0000
    }
    bool RecordsArray_OptInfo() const {
        return value >= 0xc0 && value <= 0xdf; // 0b1100'0000 - 0b1101'1111
    }
    // Optimized primitives
    bool UINT8() const {
        return value == 0x16 || value == 0x1a;
    }
    bool UINT16() const {
        return value == 0x17;
    }
    bool ZERO() const {
        return value == 0x14 || value == 0x19 || value == 0x1d;
    }
    bool ONE() const {
        return value == 0x15;
    }
    bool INT16() const {
        return value == 0x1b;
    }
    bool INT24() const {
        return value == 0x1c;
    }
    bool UINT24() const {
        return value == 0x18;
    }
    bool BOOL_FALSE() const {
        return value == 0x13;
    }
    bool BOOL_TRUE() const {
        return value ==  0x12;
    }

    // Optimized arrays
    bool UINT8_ARRAY() const {
        return value == 0x56 || ::NodeType::UINT8_ARRAY();
    }
    bool UINT16_ARRAY() const {
        return value == 0x57 || ::NodeType::UINT16_ARRAY();
    }
    bool UINT24_ARRAY() const {
        return value == 0x58;
    }
    bool INT8_ARRAY() const {
        return value == 0x5a || ::NodeType::INT8_ARRAY();
    }
    bool INT16_ARRAY() const {
        return value == 0x5b;
    }
    bool ASCII_ARRAY() const {
        return value == 0x4f;
    }
    bool UTF16_ARRAY() const {
        return value == 0x4e;
    }
};

template <class T>
inline std::vector<T> read_primitives_array(std::istream& in) {
    auto sz = read_uintvar(in);
    std::vector<T> res(sz/sizeof(T));
    in.read(reinterpret_cast<char*>(res.data()), sz);
    return res;
}

Json::Value parse_node(std::istream& in, const Params& params, const std::string& parent_node_name="");

Json::Value parse_record_opt_info(std::istream &in, const Params& params, NodeType node_type) {
    Json::Value res;
    auto b_1 = node_type.value;
    auto b_2 = read<uint8_t>(in);
    uint16_t node_index = ((b_1 & 1) << 8) | b_2;
    std::cout << params.node_names[node_index] << std::endl;
    res["Name"] = params.node_names[node_index];
    auto nodes_sz = read_uintvar(in);
    auto nodes_end = in.tellg();
    nodes_end += nodes_sz;
    Json::Value& nodes = res["Nodes"];
    for (auto i = 0; in.tellg() < nodes_end; ++i) {
        nodes[i] = parse_node(in, params, params.node_names[node_index]);
    }
    if (in.tellg() != nodes_end) {
        throw std::runtime_error("something is wrong.");
    }
    return res;
}

Json::Value parse_records_array(std::istream &in, const Params& params) {
    Json::Value res;
    auto node_index = read<uint16_t>(in);
    res["Name"] = params.node_names[node_index];
    res["Type"] = "RECORDS_ARRAY";
    in.seekg(sizeof(uint8_t), std::ios_base::cur);
    auto content_sz = read_uintvar(in);
    auto num = read_uintvar(in);
    auto content_end = static_cast<size_t>(in.tellg()) + content_sz;
    Json::Value& nodes = res["Nodes"];
    for (auto i = 0; i < num; ++i) {
        auto record_sz = read_uintvar(in);
        auto record_end = static_cast<size_t>(in.tellg()) + record_sz;
        Json::Value record{};
        for (auto node_idx = 0; in.tellg() < record_end; ++node_idx) {
            record[node_idx] = parse_node(in, params, params.node_names[node_index]);
        }
        if (in.tellg() != record_end) {
            throw std::runtime_error("something is wrong.");
        }
        nodes[i] = record;
    }
    if (in.tellg() != content_end) {
        throw std::runtime_error("something is wrong.");
    }
    return res;
}

Json::Value parse_records_array_opt_info(std::istream &in,
                                         const Params& params,
                                         NodeType node_type) {
    Json::Value res;
    auto b_1 = node_type.value;
    auto b_2 = read<uint8_t>(in);
    uint16_t node_index = ((b_1 & 1) << 8) | b_2;
    res["Name"] = params.node_names[node_index];
    res["Type"] = "RECORDS_ARRAY_OPT";
    auto content_sz = read_uintvar(in);
    auto num = read_uintvar(in);
    auto content_end = static_cast<size_t>(in.tellg()) + content_sz;
    Json::Value& nodes = res["Nodes"];
    for (auto i = 0; i < num; ++i) {
        auto record_sz = read_uintvar(in);
        auto record_end = static_cast<size_t>(in.tellg()) + record_sz;
        Json::Value record{};
        for (auto node_idx = 0; in.tellg() < record_end; ++node_idx) {
            record[node_idx] = parse_node(in, params, params.node_names[node_index]);
        }
        if (in.tellg() != record_end) {
            throw std::runtime_error("something is wrong.");
        }
        nodes[i] = record;
    }
    if (in.tellg() != content_end) {
        throw std::runtime_error("something is wrong.");
    }
    return res;
}

Json::Value parse_record(std::istream &in, const Params& params);

// for now just print whatever you find, later will save to YAML::Node
Json::Value parse_node(std::istream &in, const Params& params, const std::string& parent_node_name) {
    Json::Value res;
    auto node_type= read<NodeType>(in);
    if (node_type.Record()) {
        res = parse_record(in, params);
    } else if (node_type.Record_OptInfo()) {
        res = parse_record_opt_info(in, params, node_type);
    } else if (node_type.RecordsArray()) {
        res = parse_records_array(in, params);
    } else if (node_type.RecordsArray_OptInfo()) {
        res = parse_records_array_opt_info(in, params, node_type);
    } else if (node_type.ASCII()) {
        auto idx = read<uint32_t>(in);
        res = params.ansii_strings[idx];
    } else if (node_type.UTF16()) {
        auto idx = read<uint32_t>(in);
        res = params.utf16_strings[idx];
    } else if (node_type.UINT8()) {
        auto numb = read<uint8_t>(in);
        res = numb;
    } else if (node_type.UINT16()) {
        auto numb = read<uint16_t>(in);
        res = numb;
    } else if (node_type.INT16()) {
        auto numb = read<int16_t>(in);
        res = numb;
    } else if (node_type.INT24() || node_type.UINT24()) {
        auto bytes = read<std::array<uint8_t, 3>>(in);
        auto numb = bytes[2] + (bytes[1] << 8) + (bytes[0] << 16);
        res = numb;
    } else if (node_type.ZERO()) {
        res = 0;
    } else if (node_type.ONE()) {
        res = 1;
    } else if (node_type.BOOL_FALSE()) {
        res = false;
    } else if (node_type.BOOL_TRUE()) {
        res = true;
    } else if (node_type.UINT32_ARRAY()) {
        auto arr = read_primitives_array<uint32_t>(in);
        res = primitives_array_to_json(arr);
    } else if (node_type.UINT16_ARRAY()) {
        auto arr = read_primitives_array<uint16_t>(in);
        res = primitives_array_to_json(arr);
    } else if (node_type.ASCII_ARRAY()) {
        if (parent_node_name == "FACTION") {
            res = Json::Value(Json::arrayValue);
            auto idx_arr = read_primitives_array<uint32_t>(in);
            for (auto idx : idx_arr) {
                res.append( params.ansii_strings[idx] );
            }
        } else {
            auto sz = read_uintvar(in);
            res = "STRING ARRAY";
            in.seekg(sz, std::ios_base::cur);
        }
    } else if (node_type.UTF16_ARRAY()) {
        auto sz = read_uintvar(in);
        res = "UTF16 ARRAY";
        // TODO: keep data
        in.seekg(sz, std::ios_base::cur);
    } else if (node_type.UINT8_ARRAY()) {
        auto sz = read_uintvar(in);
        auto start = static_cast<size_t>(in.tellg());
        res = ByteArray{start, sz}.to_json();
        in.seekg(sz, std::ios_base::cur);
    } else if (node_type.BOOL_ARRAY()) {
        auto sz = read_uintvar(in);
        auto start = static_cast<size_t>(in.tellg());
        res = ByteArray{start, sz}.to_json();
        in.seekg(sz, std::ios_base::cur);
    } else if (node_type.UINT16_ARRAY()) {
        auto sz = read_uintvar(in);
        auto start = static_cast<size_t>(in.tellg());
        res = ByteArray{start, sz}.to_json();
        in.seekg(sz, std::ios_base::cur);
    } else if (node_type.UINT24_ARRAY()) {
        auto sz = read_uintvar(in);
        auto start = static_cast<size_t>(in.tellg());
        res = ByteArray{start, sz}.to_json();
        in.seekg(sz, std::ios_base::cur);
    } else if (node_type.INT16_ARRAY()) {
        auto sz = read_uintvar(in);
        auto start = static_cast<size_t>(in.tellg());
        res = "INT16 OPT ARRAY";
        in.seekg(sz, std::ios_base::cur);
    } else if (node_type.INT8_ARRAY()) {
        auto sz = read_uintvar(in);
        auto start = static_cast<size_t>(in.tellg());
        res = "INT8 OPT ARRAY";
        in.seekg(sz, std::ios_base::cur);
    } else if (node_type.UINT64_ARRAY()) {
        auto sz = read_uintvar(in);
        auto start = static_cast<size_t>(in.tellg());
        res = "INT64 PRIM ARRAY";
        in.seekg(sz, std::ios_base::cur);
    } else if (node_type.FLOAT_ARRAY()) {
        auto sz = read_uintvar(in);
        auto start = static_cast<size_t>(in.tellg());
        res = "FLOAT PRIM ARRAY";
        in.seekg(sz, std::ios_base::cur);
    } else {
        return ::parse_node(in, node_type);
    }
    return res;
}

Json::Value parse_record(std::istream &in, const Params& params) {
    Json::Value res;
    auto node_index = read<uint16_t>(in);
    auto &node_name = params.node_names[node_index];
    res["Name"] = node_name;
    std::cout << node_name << "\n";
    in.seekg(sizeof(uint8_t), std::ios_base::cur);

    auto nodes_sz = read_uintvar(in);
    std::cout << "nodes size: " << nodes_sz << '\n';
    auto nodes_end = in.tellg();
    nodes_end += nodes_sz;
    Json::Value& nodes = res["Nodes"];
    for (auto i = 0; in.tellg() < nodes_end; ++i) {
        nodes[i] = parse_node(in, params, node_name);
    }
    if (in.tellg() != nodes_end) {
        throw std::runtime_error("something is wrong.");
    }
    return res;
}

Json::Value parse_root_record(std::istream &in, const Params& params) {
    auto node_type = read<NodeType>(in);
    if (!node_type.RootRecord()) {
        throw std::runtime_error("Root node is not a SingleNode.");
    }
    return parse_record(in, params);
}

// Use the following link for reference:
// https://github.com/vasi/squashfuse/blob/94f998c58d2bb6dff00173f33140a0354adce324/decompress.c#L78
// * lzma_properties must be 5 bytes.
std::vector<uint8_t> decompress(std::istream &in,
                                ByteArray data,
                                size_t decompress_sz,
                                ByteArray lzma_properties) {

    constexpr size_t LZMA_PROPERTIES_SIZE = 5;
    constexpr size_t LZMA_UNCOMPRESSED_SIZE = 8;
    constexpr size_t LZMA_HEADER_SIZE = LZMA_PROPERTIES_SIZE + LZMA_UNCOMPRESSED_SIZE;

    if (lzma_properties.size != LZMA_PROPERTIES_SIZE) {
        throw std::runtime_error("error");
    }
    std::vector<uint8_t> uncompressed_bytes(decompress_sz);

    lzma_stream stream = LZMA_STREAM_INIT;
    auto res = lzma_alone_decoder(&stream, UINT64_MAX);
    if (res != LZMA_OK) {
        lzma_end(&stream);
        throw std::runtime_error("error");
    }

    constexpr uint8_t LZMA_HEADER_INIT_BYTE = 255;
    std::array<uint8_t, LZMA_HEADER_SIZE> lzma_header;
    std::fill(lzma_header.begin(), lzma_header.end(), LZMA_HEADER_INIT_BYTE);

    in.seekg(lzma_properties.file_start);
    in.read(reinterpret_cast<char*>(&lzma_header), lzma_properties.size);

    stream.next_out = uncompressed_bytes.data();
    stream.avail_out = uncompressed_bytes.size();
    stream.next_in = lzma_header.data();
    stream.avail_in = LZMA_HEADER_SIZE;

    res = lzma_code(&stream, LZMA_RUN);

    if (res != LZMA_OK || stream.avail_in != 0) {
        lzma_end(&stream);
        throw std::runtime_error("error");
    }

    std::vector<uint8_t> compressed_bytes(data.size);
    in.seekg(data.file_start);
    in.read(reinterpret_cast<char*>(compressed_bytes.data()), data.size);

    stream.next_out = uncompressed_bytes.data();
    stream.avail_out = uncompressed_bytes.size();
    stream.next_in = compressed_bytes.data();
    stream.avail_in = data.size;

    res = lzma_code(&stream, LZMA_FINISH);
    lzma_end(&stream);

    if (res == LZMA_OK && stream.total_out == decompress_sz && stream.avail_in == 0) {
        return uncompressed_bytes;
    }
    throw std::runtime_error("error");
}

void process_compressed_data(std::istream &in, Json::Value& val) {
    if (!val.isObject()) {
        return;
    }
    if (val.isMember("Name") && val["Name"] == "COMPRESSED_DATA") {
        auto& nodes = val["Nodes"];
        ByteArray data_ba{nodes[0]};
        auto& info = nodes[1];
        if (!(info.isMember("Name") && info["Name"] == "COMPRESSED_DATA_INFO")) {
            throw std::runtime_error("Expect nodes[1] to be COMPRESSED_DATA_INFO");
        }
        auto& info_nodes = info["Nodes"];
        auto decompress_sz = info_nodes[0].asUInt64();
        ByteArray info_ba{info_nodes[1]};

        auto decompressed_bytes = decompress(in, data_ba, decompress_sz, info_ba);
        std::stringstream stream;
        stream.write(reinterpret_cast<char*>(decompressed_bytes.data()), decompressed_bytes.size());
        std::vector<uint8_t>{}.swap(decompressed_bytes);
        stream.seekg(0, std::ios_base::beg);

        val = parse_esf(stream);
        return;
    }
    if (val.isMember("Nodes")) {
        for (auto& node : val["Nodes"]) {
            process_compressed_data(in, node);
        }
    }
}

Json::Value parse(std::istream& in, const Params& params) {
    auto res = parse_root_record(in, params);
    process_compressed_data(in, res);
    return res;
}

}