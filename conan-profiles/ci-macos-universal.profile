# Conan profile for macOS Universal (x86_64 + arm64) builds

[settings]
os=Macos
arch=x86_64  # primary; we will build universal via flags
compiler=apple-clang
compiler.version=${APPLE_CLANG_VERSION}
compiler.libcxx=libc++
build_type=Release

[options]
# OpenSSL options for universal build
openssl/*:shared=True
openssl/*:fips=True
openssl/*:enable_quic=True
openssl/*:enable_lms=True
openssl/*:enable_unit_test=True

[buildenv]
# Respect env or fall back to defaults
CC=${CC}
CXX=${CXX}
CFLAGS=${CFLAGS:- -O2 -g -arch x86_64 -arch arm64}
CXXFLAGS=${CXXFLAGS:- -O2 -g -arch x86_64 -arch arm64}
LDFLAGS=${LDFLAGS:- -arch x86_64 -arch arm64}
MACOSX_DEPLOYMENT_TARGET=${MACOSX_DEPLOYMENT_TARGET:-12.0}
SDKROOT=${SDKROOT}
DEVELOPER_DIR=${DEVELOPER_DIR}
OSSL_RUN_CI_TESTS=1
HARNESS_JOBS=${HARNESS_JOBS:-4}

[conf]
tools.env:CONAN_CPU_COUNT=${CONAN_CPU_COUNT}
tools.build:jobs=${CONAN_CPU_COUNT}

