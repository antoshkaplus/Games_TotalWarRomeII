#pragma once
#include <fstream>
#include <jsoncpp/json/json.h>


void write_to_file(const Json::Value& obj, const std::string& path) {
    std::ofstream out(path);
    Json::StyledStreamWriter().write(out, obj);
}

template<class T>
Json::Value primitives_array_to_json(const std::vector<T>& arr) {
    Json::Value res;
    for (auto a : arr) {
        res.append(a);
    }
    return res;
}