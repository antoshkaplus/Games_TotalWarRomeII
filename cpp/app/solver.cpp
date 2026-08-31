#include <iostream>
#include <boost/format.hpp>
#include "building_collection.hpp"
#include "province.hpp"
#include "solver.hpp"
#include "province_convert.hpp"
#include "cli.hpp"

namespace po = boost::program_options;

void PrintNestedException(const std::exception& e, int level = 0);

int main(int ac, const char *av[]) {
    try {
        cli::Global global;
        if (global.Handle(cli::Args{.argc=ac, .argv=av})) {
            return 0;
        }
        std::unique_ptr<cli::Cmd> cmds[] = {
                std::make_unique<cli::FindLeafsCmd>(),
                std::make_unique<cli::ResourceLeafsCmd>(),
                std::make_unique<cli::StatsCmd>(),
                std::make_unique<cli::LocalSearchCmd>()};
        bool handled = false;
        for (auto& cmd : cmds) {
            if (cmd->name() == global.command_name()) {
                cmd->Handle(global);
                handled = true;
                break;
            }
        }
        if (!handled) {
            auto msg = boost::format("command %1% is unexpected") % global.command_name();
            throw std::invalid_argument(msg.str());
        }
    } catch(std::exception& e) {
        PrintNestedException(e);
        return 1;
    } catch(...) {
        std::cerr << "Exception of unknown type!\n";
    }
}

void PrintNestedException(const std::exception& e, int level) {
    if (level == 0) {
        ant::Println(std::cerr, "Error occurred:");
        PrintNestedException(e, 1);
        return;
    }
    ant::Println(std::cerr, std::string(level, ' '), e.what());
    try {
        std::rethrow_if_nested(e);
    } catch (const std::exception& nested) {
        PrintNestedException(nested, level+1);
    } catch (...) {}
}