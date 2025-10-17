# Contributing to OpenSSL Tools

## Git Workflow - Rebase Strategy

### Daily Development

1. **Always sync with upstream before starting work**:
   ```bash
   git fetch origin
   git rebase origin/master
   ```

2. **Commit frequently with meaningful messages**:
   ```bash
   git commit -m "feat(scope): description"
   ```

3. **Before pushing, squash work-in-progress commits**:
   ```bash
   git rebase -i HEAD~n  # n = number of commits
   ```

### Branch Management

**Feature Branches** (rebase):
- Keep history linear
- Squash before creating PR
- Rebase on target branch regularly

**Integration Branches** (merge):
- Preserve complete history
- Use merge commits for cross-team work
- Document integration points

**Personal Branches** (rebase freely):
- Experiment without restrictions
- Clean up before sharing
- Squash into logical commits

### Pull Request Workflow

1. **Before opening PR**:
   ```bash
   git fetch origin
   git rebase origin/master
   git rebase -i HEAD~n  # Squash to 1-3 logical commits
   ```

2. **After PR review with new commits**:
   ```bash
   git rebase -i HEAD~n  # Squash review fixes into original commits
   git push --force-with-lease
   ```

3. **Merge strategy**:
   - Upstream PRs: Squash merge (1 commit in history)
   - Fork development: Rebase merge (linear history)

### Conflict Resolution

**When conflicts occur during rebase**:

1. Don't panic - conflicts are normal
2. Read the conflict carefully
3. Understand both versions
4. Merge intelligently, don't just pick one
5. Test after resolving
6. Use `git rebase --abort` if stuck

### Force Push Guidelines

**Safe force push**:
```bash
git push --force-with-lease origin branch-name
```

**Never force push**:
- Main/master branches
- Shared feature branches (coordinate first)
- After PR merge

**Always force push**:
- After squashing commits
- After rebasing feature branch
- On personal feature branches

### Configuration Files

**`.git/config` additions**:
```ini
[pull]
    rebase = true

[rebase]
    autoStash = true
    autoSquash = true
```

**Global git config**:
```bash
git config --global pull.rebase true
git config --global rebase.autoStash true
git config --global rebase.autoSquash true
```

## Conventional Commits

We use conventional commits for clear, structured commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types**:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

**Examples**:
```
feat(conan): consolidate CI/CD tooling as Conan python_requires package
fix(package): complete openssl-tools package method for python_requires
docs(workflows): add cross-repository integration test workflows
```

## Conan Package Development

For Conan package contributions:

1. **Test package creation**:
   ```bash
   conan create . --build=missing
   ```

2. **Validate python_requires**:
   ```bash
   conan install --requires=openssl-tools/1.0.0 --build=missing
   ```

3. **Cross-platform testing**:
   ```bash
   conan create . -s os=Windows --build=missing
   conan create . -s os=Macos --build=missing
   ```

4. **Package structure validation**:
   ```bash
   conan inspect .  # Check package metadata
   ```

## GitHub Actions Workflows

For workflow contributions:

1. **Test locally with act**:
   ```bash
   act -j validate-consumer
   ```

2. **Validate YAML syntax**:
   ```bash
   yamllint .github/workflows/
   ```

3. **Test cross-repository triggers**:
   - Verify `repository_dispatch` events work
   - Test conditional logic for different contexts

## MCP Server Development

For MCP (Model Context Protocol) server contributions:

1. **Test server functionality**:
   ```bash
   python -m mcp_project_orchestrator
   ```

2. **Validate JSON schemas**:
   ```bash
   python -c "import json; json.load(open('config.json'))"
   ```

3. **Test Cursor integration**:
   - Deploy configuration to `.cursor/`
   - Verify AI assistance works correctly

## Code Review Process

1. **Self-review**: Test your changes thoroughly
2. **Squash commits**: Clean up commit history before requesting review
3. **Clear description**: Explain what changed and why
4. **Reference issues**: Link to related issues or discussions
5. **Update documentation**: Keep docs in sync with code changes
6. **Test integration**: Verify cross-repository workflows function

## Questions?

- Check existing issues and discussions
- Review the OpenSSL Tools documentation
- Test with the OpenSSL development environment
