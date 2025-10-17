script_folder="/home/sparrow/projects/openssl-devenv/openssl-tools/build-release/conan"
echo "echo Restoring environment" > "$script_folder/deactivate_conanrunenv-release-x86_64.sh"
for v in OPENSSL_PROFILES_PATH FIPS_DATA_ROOT
do
    is_defined="true"
    value=$(printenv $v) || is_defined="" || true
    if [ -n "$value" ] || [ -n "$is_defined" ]
    then
        echo export "$v='$value'" >> "$script_folder/deactivate_conanrunenv-release-x86_64.sh"
    else
        echo unset $v >> "$script_folder/deactivate_conanrunenv-release-x86_64.sh"
    fi
done


export OPENSSL_PROFILES_PATH="/home/sparrow/.conan2/p/b/opens93e3f20b926d4/p/profiles"
export FIPS_DATA_ROOT="/home/sparrow/.conan2/p/opens4b83e3c9a0ebe/p"