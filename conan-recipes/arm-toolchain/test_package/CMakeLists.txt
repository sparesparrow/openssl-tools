cmake_minimum_required(VERSION 3.20)
project(test_package C CXX)

find_package(CMakeDeps CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
