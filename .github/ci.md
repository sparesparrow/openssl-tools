# CI/CD Architecture and Workflow Map

## 🏗️ **Architecture Overview**

This repository implements a **modular CI/CD architecture** with clear separation between fast feedback and comprehensive validation.

### **Core Principles**
- **Fast Lane**: Quick validation for PRs (5-15 minutes)
- **Weekly Exhaustive**: Full matrix coverage (scheduled)
- **Modular Workflows**: Thematic separation for maintainability
- **Upstream Parity**: Maintain security nets (fuzz, run-checker, QUIC)

## 📊 **Workflow Map**

### **🚀 Fast Lane (PR Validation)**
| Workflow | Trigger | Duration | Purpose |
|----------|---------|----------|---------|
| `basic-validation.yml` | PR (src/include/test changes) | ~10 min | Core functionality validation |
| `basic-openssl-build.yml` | PR (conanfile.py changes) | ~30 min | Conan integration test |
| `simplified-basic-validation.yml` | PR (minimal changes) | ~5 min | Quick syntax/structure check |

### **🔍 Comprehensive Validation**
| Workflow | Trigger | Duration | Purpose |
|----------|---------|----------|---------|
| `weekly-exhaustive.yml` | Schedule (weekly) | ~2-4 hours | Full matrix coverage |
| `fast-lane-ci.yml` | Manual/PR (critical paths) | ~45 min | Extended validation |
| `windows.yml` | PR (Windows changes) | ~30 min | Windows compatibility |

### **🔒 Security & Quality Nets**
| Workflow | Trigger | Duration | Purpose |
|----------|---------|----------|---------|
| `fuzz-checker.yml` | PR (crypto changes) | ~1 hour | Fuzzing validation |
| `run-checker-*.yml` | PR (test changes) | ~30 min | Test suite validation |
| `provider-compatibility.yml` | PR (provider changes) | ~45 min | Provider compatibility |
| `run_quic_interop.yml` | PR (QUIC changes) | ~1 hour | QUIC interoperability |

### **🔧 Build & Release**
| Workflow | Trigger | Duration | Purpose |
|----------|---------|----------|---------|
| `conan-ci.yml` | Manual/PR (conanfile changes) | ~1 hour | Conan package validation |
| `conan-release.yml` | Tag/Release | ~2 hours | Conan package release |
| `trigger-tools.yml` | PR (orchestration changes) | ~5 min | Cross-repo integration |

## 🎯 **Trigger Strategy**

### **File-Based Gating**
```yaml
# Fast lane triggers
- src/**/*.c
- include/**/*.h  
- test/**/*.c
- conanfile.py
- VERSION.dat

# Comprehensive triggers
- crypto/** (triggers fuzz-checker)
- ssl/** (triggers QUIC interop)
- providers/** (triggers provider-compatibility)
- .github/workflows/** (triggers all)
```

### **Matrix Strategy**
- **Fast Lane**: Minimal matrix (latest Ubuntu, basic Windows)
- **Weekly Exhaustive**: Full matrix (all OS, compilers, architectures)
- **Windows**: Split between fast (MSVC+MinGW) and comprehensive (all toolchains)

## 📈 **SLA and Performance**

### **Response Times**
- **Fast Lane**: < 15 minutes
- **Security Nets**: < 1 hour
- **Weekly Exhaustive**: < 4 hours
- **Release**: < 2 hours

### **Success Criteria**
- **Fast Lane**: 95% success rate
- **Security Nets**: 90% success rate (flaky tests managed)
- **Weekly Exhaustive**: 85% success rate

## 🔄 **Flaky Test Management**

### **Retry Strategy**
- **Max Retries**: 1 (for run-checker, QUIC tests)
- **Flaky Detection**: Auto-labeling of flaky tests
- **Issue Creation**: Automatic issue creation for persistent flakiness

### **Quarantine Process**
1. **Detection**: 3 consecutive failures with same signature
2. **Quarantine**: Move to separate workflow
3. **Investigation**: Manual review within 48 hours
4. **Resolution**: Fix or permanent quarantine

## 🛡️ **Security and Permissions**

### **Cross-Repository Integration**
- **Minimal Permissions**: GITHUB_TOKEN with explicit scopes
- **Audit Logging**: All cross-repo actions logged
- **Negative Tests**: Unauthorized trigger detection

### **Secrets Management**
- **Minimal Sharing**: Only necessary secrets between workflows
- **Rotation**: Regular secret rotation
- **Scope Limitation**: Workflow-specific secret scopes

## 📚 **Maintenance Guidelines**

### **Adding New Workflows**
1. **Identify Category**: Fast lane, comprehensive, or security net
2. **Define Triggers**: File-based gating
3. **Set SLA**: Duration and success criteria
4. **Update Documentation**: This file and workflow comments

### **Modifying Existing Workflows**
1. **Impact Assessment**: Effect on SLA and success rates
2. **Testing**: Validate in feature branch
3. **Documentation**: Update relevant sections
4. **Communication**: Notify team of changes

### **Upstream Synchronization**
- **Monthly Review**: Check upstream workflow changes
- **Security Updates**: Immediate adoption of security-related changes
- **Feature Parity**: Maintain compatibility with upstream security nets

## 🚨 **Troubleshooting**

### **Common Issues**
- **Runner Overload**: Check queue status, consider workflow prioritization
- **Flaky Tests**: Review quarantine list, investigate patterns
- **Permission Errors**: Verify GITHUB_TOKEN scopes
- **Cross-Repo Failures**: Check trigger permissions and audit logs

### **Escalation Process**
1. **Level 1**: Workflow maintainer (immediate)
2. **Level 2**: CI/CD team (within 4 hours)
3. **Level 3**: Platform team (within 24 hours)

## 📊 **Metrics and Monitoring**

### **Key Metrics**
- **Success Rate**: Per workflow category
- **Duration**: Average and P95
- **Queue Time**: Runner availability
- **Flaky Rate**: Percentage of flaky tests

### **Reporting**
- **Weekly**: CI/CD health report
- **Monthly**: Performance trends and recommendations
- **Quarterly**: Architecture review and optimization

---

**Last Updated**: 2025-10-10  
**Maintainer**: CI/CD Team  
**Review Cycle**: Monthly
