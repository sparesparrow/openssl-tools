# Conan profile for CI Linux GCC builds
# Used for consistent builds across CI environments

[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
build_type=Release

[options]
# OpenSSL specific options for CI
openssl/*:shared=True
openssl/*:fips=True
openssl/*:enable_quic=True
openssl/*:enable_lms=True
openssl/*:enable_demos=True
openssl/*:enable_h3demo=True
openssl/*:enable_unit_test=True
openssl/*:enable_buildtest_c++=True

# Dependency options
zlib/*:shared=False

[buildenv]
# Build environment variables
CC=gcc-11
CXX=g++-11
CFLAGS=-O2 -g -fstack-protector-strong
CXXFLAGS=-O2 -g -fstack-protector-strong
LDFLAGS=-Wl,-z,relro,-z,now

# OpenSSL CI specific
OSSL_RUN_CI_TESTS=1
HARNESS_JOBS=4

[conf]
# Conan configuration for CI
tools.system.package_manager:mode=install
tools.system.package_manager:sudo=True
tools.env:CONAN_CPU_COUNT=4

# Cache configuration
tools.cmake.cmaketoolchain:generator=Unix Makefiles
tools.build:jobs=4
tools.build:verbosity=quiet

# Security settings
tools.system.package_manager:allow_sudo=True