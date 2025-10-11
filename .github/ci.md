# CI/CD Architecture and Workflow Map

## 🏗️ **Architecture Overview**

This repository implements a **modern CI/CD architecture** for OpenSSL package management using Conan 2.0, with automated failure recovery and comprehensive validation.

### **Core Principles**
- **OpenSSL Package Building**: Conan-based package creation and publishing
- **Multi-Platform Support**: Linux, Windows, macOS with various compilers
- **Automated Failure Recovery**: Cursor-agent integration for intelligent fixes
- **Security-First**: Comprehensive security scanning and validation
- **Binary-First**: Optimized for package consumption and distribution

## 📊 **Workflow Map**

### **🚀 Primary Build & Publish**
| Workflow | Trigger | Duration | Purpose |
|----------|---------|----------|---------|
| `openssl-build-publish.yml` | PR/Push (conanfile.py changes) | ~45 min | OpenSSL package build & publish |
| `binary-first-ci.yml` | PR/Push (conanfile.py changes) | ~1 hour | Modern CI/CD with Conan 2.0 |

### **🔧 Conan Package Management**
| Workflow | Trigger | Duration | Purpose |
|----------|---------|----------|---------|
| `conan-ci.yml` | PR/Push (conanfile.py changes) | ~30 min | Conan package validation |
| `conan-ci-enhanced.yml` | PR/Push (conanfile.py changes) | ~45 min | Enhanced Conan CI with Artifactory |
| `conan-pr-tests.yml` | PR (conanfile.py changes) | ~20 min | PR-specific Conan testing |
| `conan-nightly.yml` | Schedule (daily) | ~1 hour | Nightly Conan builds |
| `modern-ci.yml` | PR/Push (conanfile.py changes) | ~1 hour | Modern CI with dependency management |

### **🔍 Basic Validation & Testing**
| Workflow | Trigger | Duration | Purpose |
|----------|---------|----------|---------|
| `basic-integration-test.yml` | PR/Push (conanfile.py changes) | ~10 min | Basic integration validation |
| `basic-openssl-integration-test.yml` | PR/Push (conanfile.py changes) | ~15 min | OpenSSL integration testing |
| `ci-quick-fix.yml` | PR/Push (conanfile.py changes) | ~5 min | Quick CI fixes |
| `comprehensive-override.yml` | Manual | ~5 min | Comprehensive override |
| `simple-success-override.yml` | Manual | ~5 min | Simple success override |
| `optimized-basic-ci.yml` | PR/Push (conanfile.py changes) | ~20 min | Optimized basic CI |
| `baseline-ci.yml` | PR/Push (conanfile.py changes) | ~15 min | Baseline CI validation |
| `compiler-zoo.yml` | PR/Push (conanfile.py changes) | ~1 hour | Multi-compiler testing |

### **🔒 Security & Quality**
| Workflow | Trigger | Duration | Purpose |
|----------|---------|----------|---------|
| `static-analysis.yml` | Schedule/PR (conanfile.py changes) | ~30 min | Static code analysis |
| `static-analysis-on-prem.yml` | Schedule/PR (conanfile.py changes) | ~45 min | On-premises static analysis |
| `style-checks.yml` | PR (conanfile.py changes) | ~10 min | Coding style validation |
| `coveralls.yml` | PR (conanfile.py changes) | ~15 min | Code coverage reporting |
| `fuzz-checker.yml` | PR/Push (conanfile.py changes) | ~1 hour | Fuzzing validation |

## 🎯 **Trigger Strategy**

### **File-Based Gating**
```yaml
# Primary triggers
- conanfile.py
- conanfile.txt
- conan-profiles/**
- src/**
- include/**
- scripts/**

# Workflow-specific triggers
- .github/workflows/** (triggers all)
- test/** (triggers testing workflows)
```

### **Matrix Strategy**

#### Strategy Categories

**Fast Lane (PR checks)**
- Minimal matrix: ubuntu-22.04 + windows-2022
- Latest stable versions only
- Quick feedback (<10 min)

**Comprehensive (main branch)**  
- Full matrix: 5 platforms × multiple versions
- All supported configurations
- Quality gate before release

**Security Net (scheduled)**
- Extended matrix with edge cases
- Nightly comprehensive testing
- Early detection of regressions

## 📈 **SLA and Performance**

### **Response Times**
- **Basic Validation**: < 15 minutes
- **Conan Package Build**: < 45 minutes
- **Security Scanning**: < 1 hour
- **Comprehensive Testing**: < 2 hours

### **Success Criteria**
- **Basic Validation**: 95% success rate
- **Package Building**: 90% success rate
- **Security Scanning**: 95% success rate
- **Automated Recovery**: 80% of failures auto-fixed

## 🤖 **Automated Failure Recovery**

### **Cursor-Agent Integration**
- **Automatic Analysis**: Failed jobs trigger intelligent analysis
- **Minimal Fixes**: Automated application of safe, minimal changes
- **PR Comments**: Automatic feedback on fixes applied
- **Timeout Protection**: 5-minute timeout to prevent infinite loops

### **Recovery Process**
1. **Failure Detection**: Job failure triggers cursor-agent
2. **Log Analysis**: AI analyzes failure logs and context
3. **Fix Generation**: Proposes minimal, safe fixes
4. **Auto-Apply**: Commits and pushes fixes automatically
5. **Notification**: Comments on PR with analysis and changes

## 🛡️ **Security and Permissions**

### **Required Secrets**
| Secret | Purpose | Required For |
|--------|---------|--------------|
| `CURSOR_API_KEY` | Automated failure analysis | All workflows with failure recovery |
| `CONAN_REMOTE_URL` | Custom Conan remote | Package publishing (optional) |
| `CONAN_USER` | Conan remote authentication | Package publishing (optional) |
| `CONAN_PASSWORD` | Conan remote authentication | Package publishing (optional) |
| `ARTIFACTORY_URL` | Artifactory integration | Enhanced Conan workflows (optional) |
| `ARTIFACTORY_USERNAME` | Artifactory authentication | Enhanced Conan workflows (optional) |
| `ARTIFACTORY_PASSWORD` | Artifactory authentication | Enhanced Conan workflows (optional) |
| `COVERITY_TOKEN` | Coverity static analysis | Static analysis workflows (optional) |

### **Default Behavior**
- **GitHub Packages**: Default Conan remote (uses GITHUB_TOKEN)
- **GitHub Actor**: Default Conan user (uses github.actor)
- **Fallback Upload**: Automatic fallback to GitHub Packages if custom remote fails

## 📚 **Maintenance Guidelines**

### **Adding New Workflows**
1. **Identify Category**: Build, validation, security, or quality
2. **Define Triggers**: File-based gating (conanfile.py, conan-profiles/, etc.)
3. **Set SLA**: Duration and success criteria
4. **Add Failure Recovery**: Include cursor-agent integration
5. **Update Documentation**: This file and workflow comments

### **Modifying Existing Workflows**
1. **Impact Assessment**: Effect on SLA and success rates
2. **Testing**: Validate in feature branch
3. **Documentation**: Update relevant sections
4. **Communication**: Notify team of changes

### **OpenSSL Source Integration**
- **Source Cloning**: Workflows clone from github.com/sparesparrow/openssl
- **Conan Integration**: Use conanfile.py for package building
- **Profile Management**: Use conan-profiles/ for build configurations
- **Package Publishing**: Upload to configurable remotes with GitHub Packages fallback

## 🚨 **Troubleshooting**

### **Common Issues**
- **OpenSSL Clone Failures**: Check network connectivity and repository access
- **Conan Profile Errors**: Verify conan-profiles/ directory structure
- **Package Upload Failures**: Check remote configuration and credentials
- **Cursor-Agent Timeouts**: Review CURSOR_API_KEY and timeout settings
- **Permission Errors**: Verify GITHUB_TOKEN scopes and secret access

### **Automated Recovery**
- **Failure Analysis**: Cursor-agent automatically analyzes failed jobs
- **Fix Application**: Safe, minimal fixes are applied automatically
- **PR Comments**: Detailed analysis and fix information posted to PRs
- **Manual Override**: Disable automated recovery by removing CURSOR_API_KEY

### **Escalation Process**
1. **Level 1**: Automated recovery via cursor-agent (immediate)
2. **Level 2**: Workflow maintainer (within 1 hour)
3. **Level 3**: CI/CD team (within 4 hours)

## 📊 **Metrics and Monitoring**

### **Key Metrics**
- **Success Rate**: Per workflow category
- **Duration**: Average and P95
- **Queue Time**: Runner availability
- **Automated Recovery Rate**: Percentage of failures auto-fixed
- **Package Build Success**: Conan package creation success rate

### **Reporting**
- **Weekly**: CI/CD health report with automated recovery statistics
- **Monthly**: Performance trends and package build metrics
- **Quarterly**: Architecture review and optimization

## 📁 **Workflow Organization**

### **Enabled Workflows** (`.github/workflows/`)
- **4 workflows** currently enabled and adapted for openssl-tools
- **Primary focus**: OpenSSL package building and publishing
- **Automated failure recovery** integrated throughout

### **Archived Workflows** (`.github/workflows-backup/`)
- **96 workflows** archived and organized by category
- **Legacy OpenSSL**: Upstream workflows incompatible with Conan 2.0
- **Upstream-only**: OpenSSL source repository specific
- **Experimental**: PR #6 development iterations

---

**Last Updated**: 2025-10-11  
**Maintainer**: CI/CD Team  
**Review Cycle**: Monthly  
**Status**: 4 workflows enabled, automated failure recovery active