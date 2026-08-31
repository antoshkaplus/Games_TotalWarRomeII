#pragma once
#include <array>
#include <optional>
#include <span>
#include <boost/format.hpp>
#include "stats.hpp"

struct Building {
    std::string name;
    std::optional<std::string> name_alias;
    std::optional<std::string> need_resource;
    std::optional<std::string> parent;
    Stats stats;
    // resources have faction wide stats
    Stats faction_stats;
    bool resource = false;
};
