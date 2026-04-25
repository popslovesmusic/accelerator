cmake_minimum_required(VERSION 3.20)

project(analog_runtime_r2b LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(analog_runtime_r2b_probe
    src/engine_r2b_vector.cpp
    tests/vector_engine_probe_main.cpp
)

target_include_directories(analog_runtime_r2b_probe
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

if(MSVC)
    target_compile_options(analog_runtime_r2b_probe PRIVATE /W4 /permissive-)
else()
    target_compile_options(analog_runtime_r2b_probe PRIVATE -Wall -Wextra -Wpedantic)
endif()
