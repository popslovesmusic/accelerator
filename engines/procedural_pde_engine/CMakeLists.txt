cmake_minimum_required(VERSION 3.10)
project(procedural_pde_engine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

add_executable(procedural_pde_engine
    src/main.cpp
    src/engine_2d.cpp
    src/engine_3d.cpp
)
