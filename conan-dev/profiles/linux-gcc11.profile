[settings]
os=Linux
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
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
CC=gcc-11
CXX=g++-11
