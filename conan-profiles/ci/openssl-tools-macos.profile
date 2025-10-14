[settings]
os=Macos
compiler=apple-clang
compiler.version=14
compiler.libcxx=libc++
build_type=Release
arch=x86_64

[options]
openssl-tools:enable_review_tools=True
openssl-tools:enable_release_tools=True
openssl-tools:enable_statistics=True
openssl-tools:enable_github_integration=True
openssl-tools:enable_gitlab_integration=False
openssl-tools:enable_api_integration=True

[env]
CONAN_CPU_COUNT=4