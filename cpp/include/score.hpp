#pragma once
#include "stats.hpp"

struct Constraints {
    int min_food;
    int min_order;

    double food_deficit_penalty;
    double order_deficit_penalty;
};

struct Score {
    Constraints c;

    Score(const Constraints& c) : c(c) {}

    double operator()(const Stats& stats) const {
        return stats.wealth() + std::min(stats.food - c.min_food, 0) * c.food_deficit_penalty
                       + std::min(stats.order - c.min_order, 0) * c.order_deficit_penalty;
    }
};