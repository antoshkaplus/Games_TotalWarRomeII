#pragma once
#include <fstream>
#include <jsoncpp/json/json.h>


Json::Value parse_esf(std::istream& in);