[settings]
os=Windows
arch=x86_64
compiler=msvc
compiler.version=193
compiler.runtime=dynamic
build_type=Release

[options]
*:shared=True
*:fips=True
*:enable_fips_module=True

[conf]
tools.cmake.cmaketoolchain:generator=Visual Studio 17 2022
tools.microsoft.msbuild:max_cpu_count=8
