#pragma once
#include <jsoncpp/json/json.h>


struct ByteArray {
    size_t file_start;
    size_t size;

    ByteArray() = default;
    ByteArray(size_t file_start, size_t size) :
        file_start(file_start),
        size(size) {}

    ByteArray(const Json::Value& val) :
        file_start(val["fileStart"].asUInt64()),
        size(val["size"].asUInt64()) {}

    Json::Value to_json() {
        Json::Value res;
        res["fileStart"] = file_start;
        res["size"] = size;
        return res;
    }
};