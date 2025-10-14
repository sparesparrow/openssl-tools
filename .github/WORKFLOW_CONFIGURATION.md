# GitHub Actions Workflow Configuration

## Environment Variables

The build-and-publish workflow uses the following environment variables:

### `CONAN_REPOSITORY_NAME`
- **Default**: `sparesparrow-conan`
- **Purpose**: Identifies the Cloudsmith Conan repository name
- **Usage**: Used in `conan remote add` and `conan upload` commands
- **How to override**: Set in workflow `env:` block if using a different repository

### `CONAN_REPOSITORY_URL`
- **Default**: `https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/`
- **Purpose**: Complete URL to the Cloudsmith Conan repository
- **Usage**: Used when adding the remote to Conan configuration

### `PYTHON_VERSION`
- **Default**: `3.12`
- **Purpose**: Python version for running Conan and build scripts
- **Usage**: Specified in `actions/setup-python` step

## Required Secrets

### `CLOUDSMITH_API_KEY`
- **Required for**: Publishing packages to Cloudsmith (main branch and tags only)
- **How to configure**:
  1. Go to repository Settings > Secrets and variables > Actions
  2. Click "New repository secret"
  3. Name: `CLOUDSMITH_API_KEY`
  4. Value: Your Cloudsmith API key
- **Security**: The workflow includes a preflight check that fails with a clear error message if this secret is missing on main branch pushes

## Workflow Jobs

### 1. `security-scan`
- **Purpose**: Run CodeQL security analysis on Python code
- **Runs on**: All pushes and PRs
- **Permissions**: Requires `security-events: write` for CodeQL
- **Output**: Security findings in GitHub Security tab

### 2. `lint-test`
- **Purpose**: Validate code quality and package definition
- **Runs on**: All pushes and PRs
- **Checks**:
  - Bandit security scan for Python code
  - Pylint code quality checks
  - Conanfile syntax validation
- **Artifacts**: Uploads `bandit-report.json`

### 3. `build-and-publish`
- **Purpose**: Build Conan package and publish to Cloudsmith
- **Depends on**: `security-scan` and `lint-test` must pass
- **Strategy**: Fail-fast disabled to allow all matrix builds to complete
- **Features**:
  - Conan cache persistence (speeds up repeated builds)
  - SBOM generation (CycloneDX format)
  - Deployment bundle creation (for non-Conan users)
  - Smart upload strategy based on branch/event

## Upload Strategy

The workflow implements different upload behaviors based on the trigger:

### Pull Requests
- **Behavior**: Dry-run (logs command but doesn't upload)
- **Command**: `conan upload ... --only-recipe`
- **Purpose**: Verify package can be created without publishing

### Main Branch Pushes
- **Behavior**: Full upload with all dependencies
- **Command**: `conan upload ... --all --confirm`
- **Requirements**: 
  - Branch must be `main`
  - Repository must be `sparesparrow/openssl-tools` (no forks)
  - `CLOUDSMITH_API_KEY` must be configured

### Tag Pushes (v*)
- **Behavior**: Full upload with all dependencies
- **Command**: `conan upload ... --all --confirm`
- **Requirements**:
  - Tag must start with `v` (e.g., `v1.0.0`)
  - Repository must be `sparesparrow/openssl-tools` (no forks)
  - `CLOUDSMITH_API_KEY` must be configured

## Caching

The workflow caches `~/.conan2` directory to speed up CI:
- **Cache key**: `conan-{os}-{hash(conanfile.py, profiles)}`
- **Restore keys**: `conan-{os}-` (partial match fallback)
- **Invalidation**: Cache updates when conanfile.py or any profile changes
- **Speed improvement**: ~50-70% faster on cache hits

## Artifacts

The workflow produces the following artifacts:

### 1. `bandit-report`
- **Format**: JSON
- **Retention**: 90 days (default)
- **Content**: Security scan results from bandit

### 2. `sbom-reports`
- **Format**: JSON (CycloneDX)
- **Retention**: 90 days
- **Content**: 
  - `sbom-python.json`: Python dependencies SBOM
  - `sbom-package.json`: Package-level SBOM with Conan dependencies

### 3. `deployment-bundle`
- **Format**: tar.gz
- **Retention**: 30 days
- **Content**: Complete tools bundle for non-Conan users
- **Usage**: Extract and use scripts directly without Conan

## Fork Safety

The workflow includes protections against accidental publishing from forks:

```yaml
if: |
  github.event_name == 'push' &&
  github.ref == 'refs/heads/main' &&
  github.repository == 'sparesparrow/openssl-tools'
```

This ensures packages are only uploaded from the official repository.

## Customization

To customize the workflow for your own repository:

1. **Change repository names**:
   ```yaml
   env:
     CONAN_REPOSITORY_NAME: your-org-conan
     CONAN_REPOSITORY_URL: https://conan.cloudsmith.io/your-org/your-repo/
   ```

2. **Update fork protection**:
   ```yaml
   github.repository == 'your-org/your-repo'
   ```

3. **Configure Cloudsmith credentials**:
   - Add your `CLOUDSMITH_API_KEY` secret
   - Update username in `conan remote login` command

4. **Adjust retention periods**:
   - Modify `retention-days` in artifact upload steps
   - Default SBOM: 90 days
   - Default bundle: 30 days

## Troubleshooting

### Error: "CLOUDSMITH_API_KEY secret is not set"
- **Cause**: Secret not configured in repository settings
- **Fix**: Add the secret as described in "Required Secrets" section

### Cache misses on every run
- **Cause**: Profiles or conanfile.py changing frequently
- **Fix**: Normal behavior if files are modified; cache will still help with dependencies

### Upload fails from fork
- **Cause**: Fork protection is working as intended
- **Fix**: Not an error - forks should not publish to official repository

### CodeQL fails
- **Cause**: Security vulnerabilities detected or configuration issues
- **Fix**: Review Security tab findings and address issues

## Migration from Old Workflow

If migrating from the previous simpler workflow:

1. **New jobs**: `security-scan` and `lint-test` are new prerequisites
2. **Environment variables**: Now centralized in `env:` block
3. **Caching**: Automatically speeds up subsequent builds
4. **SBOM**: Now generated automatically on every build
5. **Artifacts**: Multiple artifacts are now produced (SBOM, bundle, reports)
6. **Upload logic**: More sophisticated with branch-aware behavior
