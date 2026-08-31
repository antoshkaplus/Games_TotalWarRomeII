#pragma once

#include <vector>


using Int = int;

inline bool NextCombination(std::vector<Int>& selection, Int element_count) {
    Int i = selection.size()-1;
    // max value for ith selection
    Int k = element_count-1;
    while (i >= 0 && selection[i] == k) {
        --i;
        --k;
    }
    if (i < 0) {
        return false;
    }
    ++selection[i];
    std::iota(selection.begin() + i + 1, selection.end(), selection[i]+1);
    return true;
}

inline uint64_t CombinationsCount(int select_count, int element_count) {
    uint64_t t = 1;
    for (auto k = element_count-select_count+1; k <= element_count; ++k) {
        t *= k;
    }
    for (auto k = 2; k <= select_count; ++k) {
        t /= k;
    }
    return t;
}
