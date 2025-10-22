# Conan profile for sanitizer builds in CI
# Used for memory safety testing

[settings]
os=Linux
arch=x86_64
compiler=clang
compiler.version=15
compiler.libcxx=libstdc++11
build_type=Debug

[options]
# OpenSSL sanitizer options
openssl/*:shared=False
openssl/*:fips=True
openssl/*:enable_quic=True
openssl/*:enable_lms=True
openssl/*:enable_unit_test=True
openssl/*:enable_crypto_mdebug=True

# Enable sanitizers
openssl/*:enable_asan=True
openssl/*:enable_ubsan=True
openssl/*:enable_msan=False  # Memory sanitizer requires special setup
openssl/*:enable_tsan=False  # Thread sanitizer conflicts with others

# Crypto options for thorough testing
openssl/*:enable_weak_ssl_ciphers=True
openssl/*:enable_ssl3=True
openssl/*:enable_ssl3_method=True
openssl/*:no_rc5=False
openssl/*:no_md2=False

[buildenv]
CC=clang-15
CXX=clang++-15
CFLAGS=-g -O1 -fsanitize=address,undefined -fno-optimize-sibling-calls
CXXFLAGS=-g -O1 -fsanitize=address,undefined -fno-optimize-sibling-calls
LDFLAGS=-fsanitize=address,undefined

# Sanitizer runtime options
ASAN_OPTIONS=detect_leaks=1:abort_on_error=1:check_initialization_order=1
UBSAN_OPTIONS=print_stacktrace=1:abort_on_error=1

# OpenSSL CI specific
OSSL_RUN_CI_TESTS=1
HARNESS_JOBS=2  # Reduced for sanitizer builds
OPENSSL_TEST_RAND_ORDER=0

[conf]
tools.system.package_manager:mode=install
tools.system.package_manager:sudo=True
tools.env:CONAN_CPU_COUNT=2  # Reduced for sanitizer overhead
tools.build:jobs=2