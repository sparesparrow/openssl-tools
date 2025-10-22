script_folder="/home/sparrow/projects/openssl-devenv/openssl-tools"
echo "echo Restoring environment" > "$script_folder/deactivate_conanrunenv-release-x86_64.sh"
for v in OPENSSL_TOOLS_ROOT OPENSSL_TOOLS_SCRIPTS OPENSSL_TOOLS_PROFILES OPENSSL_TOOLS_DOCKER OPENSSL_TOOLS_MCP OPENSSL_TOOLS_CURSOR_CONFIG PATH
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


export OPENSSL_TOOLS_ROOT="/home/sparrow/.conan2/p/b/opense2abf90747ea3/p"
export OPENSSL_TOOLS_SCRIPTS="/home/sparrow/.conan2/p/b/opense2abf90747ea3/p/scripts"
export OPENSSL_TOOLS_PROFILES="/home/sparrow/.conan2/p/b/opense2abf90747ea3/p/profiles"
export OPENSSL_TOOLS_DOCKER="/home/sparrow/.conan2/p/b/opense2abf90747ea3/p/docker"
export OPENSSL_TOOLS_MCP="/home/sparrow/.conan2/p/b/opense2abf90747ea3/p/openssl_tools/automation/ai_agents"
export OPENSSL_TOOLS_CURSOR_CONFIG="/home/sparrow/.conan2/p/b/opense2abf90747ea3/p/.cursor"
export PATH="/home/sparrow/.conan2/p/b/opense2abf90747ea3/p/scripts:$PATH"