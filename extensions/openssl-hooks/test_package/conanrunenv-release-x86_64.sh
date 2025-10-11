script_folder="/home/sparrow/projects/openssl-tools/extensions/openssl-hooks/test_package"
echo "echo Restoring environment" > "$script_folder/deactivate_conanrunenv-release-x86_64.sh"
for v in OPENSSL_HOOKS_VERSION OPENSSL_HOOKS_DIR
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


export OPENSSL_HOOKS_VERSION="1.0.0"
export OPENSSL_HOOKS_DIR="/home/sparrow/.conan2/p/b/opens9c860a595311a/p/hooks"