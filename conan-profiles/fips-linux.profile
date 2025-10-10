[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
build_type=Release

[options]
*:shared=True
*:fPIC=True
*:fips=True
*:enable_fips_module=True

[conf]
tools.system.package_manager:mode=install
tools.system.package_manager:sudo=True
