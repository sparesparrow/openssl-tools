cmake_minimum_required(VERSION 3.15)
project(test_openssl)

# Set C standard
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Find OpenSSL
find_package(OpenSSL REQUIRED)

# Create test executable
add_executable(test_openssl test_openssl.c)

# Link with OpenSSL libraries
target_link_libraries(test_openssl 
    OpenSSL::SSL 
    OpenSSL::Crypto
)

# Set compile definitions for OpenSSL
target_compile_definitions(test_openssl PRIVATE
    OPENSSL_IS_OPENSSL3
)

# Include directories
target_include_directories(test_openssl PRIVATE
    ${OPENSSL_INCLUDE_DIR}
)

# Compiler-specific options
if(MSVC)
    target_compile_options(test_openssl PRIVATE /W4)
else()
    target_compile_options(test_openssl PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Set output directory
set_target_properties(test_openssl PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)