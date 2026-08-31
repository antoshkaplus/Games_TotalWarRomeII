cmake_minimum_required(VERSION 3.30)
project(cpp)

set(CMAKE_CXX_STANDARD 26)
string(CONCAT CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++26 -Werror"
        " -Wno-unused-local-typedefs -Wno-error=char-subscripts -Wno-char-subscripts -Wno-unused-result -Wno-error=shadow" )

link_directories("/usr/local/lib")
include_directories("./include")
include_directories("/usr/local/include")

find_package(Boost REQUIRED CONFIG COMPONENTS log)

add_library(solver src/solver.cpp)
target_link_libraries(solver yaml-cpp Boost::log)

add_executable(solver_ex app/solver.cpp)
target_link_libraries(solver_ex boost_program_options solver)

add_executable(save_parser app/save_parser.cpp src/save_parser/esf_parser.cpp)
target_link_libraries(save_parser boost_program_options jsoncpp lzma)