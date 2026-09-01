#pragma once
#include <vector>
#include <istream>


struct Entry {
    std::u16string key;
    std::u16string value;
};


std::vector<Entry> parse_loc(std::istream& in);