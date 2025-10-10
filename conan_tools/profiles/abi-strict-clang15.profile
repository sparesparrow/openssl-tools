# ABI-Strict Clang 15 Profile
# Ensures ABI compatibility and consistency

[settings]
os=Linux
arch=x86_64
compiler=clang
compiler.version=15
compiler.libcxx=libstdc++11
build_type=Release

[conf]
# Strict ABI enforcement
tools.env:CC=/usr/bin/clang-15
tools.env:CXX=/usr/bin/clang++-15
tools.env:CMAKE_C_COMPILER=/usr/bin/clang-15
tools.env:CMAKE_CXX_COMPILER=/usr/bin/clang++-15

# ABI-specific flags
tools.env:CFLAGS=-D_GLIBCXX_USE_CXX11_ABI=1 -fPIC -stdlib=libstdc++
tools.env:CXXFLAGS=-D_GLIBCXX_USE_CXX11_ABI=1 -fPIC -std=c++17 -stdlib=libstdc++
tools.env:LDFLAGS=-Wl,--as-needed -stdlib=libstdc++

# Link-time optimization for performance
tools.env:CMAKE_INTERPROCEDURAL_OPTIMIZATION=ON
tools.env:CMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG -flto

# Ensure consistent stdlib
tools.cmake.cmaketoolchain:find_builddirs=True

# Compiler cache
tools.env:CCACHE_DIR=/cache/ccache
tools.env:CCACHE_MAXSIZE=5G

[buildenv]
CC=/usr/bin/clang-15
CXX=/usr/bin/clang++-15
AR=/usr/bin/llvm-ar-15
RANLIB=/usr/bin/llvm-ranlib-15

# Force libstdc++ usage
CXXFLAGS=-stdlib=libstdc++
LDFLAGS=-stdlib=libstdc++