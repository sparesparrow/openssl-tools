# OpenSSL Two-Repository CI/CD Implementation Plan

## Executive Summary

Implement modern CI/CD pipeline for OpenSSL with two-repository architecture:
- **sparesparrow/openssl**: Source code + basic validation
- **sparesparrow/openssl-tools**: Comprehensive CI/CD orchestration

**Strategy**: Hybrid approach balancing speed, cost-efficiency, and production safety.

## Design Decisions (Based on Analysis)

### 1. PR Created in openssl → **Option C (Hybrid)**
- Fast validation in openssl repo (3-5 min)
- Trigger comprehensive builds in openssl-tools via `repository_dispatch`
- Parallel execution for quick feedback + thorough validation

### 2. PR Merged to Master → **Option C (Build + Manual Approval)**
- Automated full build + testing in openssl-tools
- Auto-publish to staging (GitHub Packages staging namespace)
- Manual approval gate for production release

### 3. Commit to Non-Master Branch → **Option B (Lightweight)**
- Syntax validation, linting, quick tests only
- Optimize CI minutes, full validation at PR stage

### 4. Nightly Builds → **Option D (Comprehensive)**
- Full platform matrix (Linux x86/ARM, Windows, macOS)
- Security scans, performance benchmarks, dependency updates
- Runs at 2 AM UTC (off-peak)

### 5. Cross-Repo Communication → **Option A (repository_dispatch + Status API)**
- openssl triggers openssl-tools via `repository_dispatch`
- openssl-tools reports back via GitHub Commit Status API
- Clean separation of concerns

### 6. Artifact Publishing → **Option C (Two-Tier)**
- Master commits → GitHub Packages staging namespace
- Tagged releases → GitHub Packages production + optional Artifactory/GHCR
- Primary: GitHub Packages, fallback: JFrog Artifactory / GHCR Docker

### 7. Test Strategy → **Option A (Pyramidal)**
- PR: Fast unit tests (~5-8 min)
- Master: Unit + integration tests (~20-25 min)
- Nightly: Comprehensive suite including fuzz tests (~2-4 hours)

### 8. Failure Handling → **Option D (AI Agent + Manual)**
- Block PR merge on failure
- AI agent (from PR #17) analyzes logs, suggests fixes
- Manual review for complex failures
- GitHub Issues auto-created with AI analysis

## Workflow Diagrams (Mermaid)

### Diagram 1: PR Created in openssl

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GH as GitHub PR
    participant OSS as openssl repo
    participant OST as openssl-tools repo
    participant GHP as GitHub Packages

    Dev->>GH: Create PR
    activate GH
    GH->>OSS: Trigger pr-validation.yml
    activate OSS
    
    par Fast Validation (3-5 min)
        OSS->>OSS: Lint & Format Check
        OSS->>OSS: Syntax Validation
        OSS->>OSS: Single Platform Build
        OSS->>OSS: Quick Unit Tests
    end
    
    OSS->>GH: Report Fast Check Status
    
    alt Fast Checks Pass
        OSS->>OST: repository_dispatch<br/>(pr-validation event)
        activate OST
        
        par Comprehensive Builds (30-45 min)
            OST->>OST: Linux x86_64 Build + Tests
            OST->>OST: Linux ARM64 Build + Tests
            OST->>OST: Windows x64 Build + Tests
            OST->>OST: macOS Build + Tests
        end
        
        OST->>GHP: Upload Test Artifacts
        OST->>GH: Report Status via<br/>Commit Status API
        deactivate OST
    else Fast Checks Fail
        OSS->>GH: Block PR (Red Status)
        OSS->>Dev: Notify (GitHub + Email)
    end
    
    deactivate OSS
    deactivate GH
```

### Diagram 2: PR Merged to Master in openssl

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GH as GitHub
    participant OSS as openssl/master
    participant OST as openssl-tools
    participant GHP as GitHub Packages
    participant Human as Release Manager

    Dev->>GH: Merge PR to master
    activate GH
    GH->>OSS: Trigger release-build.yml
    activate OSS
    
    OSS->>OST: repository_dispatch<br/>(master-merge event)
    deactivate OSS
    activate OST
    
    par Full Release Build (45-60 min)
        OST->>OST: Build All Platforms
        OST->>OST: Run Integration Tests
        OST->>OST: Security Scans<br/>(SAST, Dependency Check)
        OST->>OST: Generate SBOM
        OST->>OST: Package for Conan
    end
    
    OST->>GHP: Publish to Staging<br/>(namespace: staging/*)
    OST->>GH: Update Commit Status
    OST->>GH: Create Deployment<br/>(Environment: staging)
    
    alt All Checks Pass
        OST->>Human: Request Production<br/>Approval (GitHub Environment)
        Human->>GH: Approve Deployment
        activate GH
        GH->>OST: Trigger production-deploy.yml
        OST->>GHP: Publish to Production<br/>(namespace: production/*)
        OST->>OST: Optional: Sync to<br/>Artifactory/GHCR
        OST->>GH: Deployment Complete
        deactivate GH
    else Checks Fail
        OST->>Dev: Notify Failure
        OST->>GH: Create Issue<br/>(AI Analysis Attached)
    end
    
    deactivate OST
    deactivate GH
```

### Diagram 3: Commit to Non-Master Branch in openssl

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GH as GitHub
    participant OSS as openssl/feature-branch

    Dev->>GH: Push to feature branch
    activate GH
    GH->>OSS: Trigger lightweight-check.yml
    activate OSS
    
    par Lightweight Checks (< 2 min)
        OSS->>OSS: Perl Syntax Check
        OSS->>OSS: Code Linting
        OSS->>OSS: Basic Compilation<br/>(Single Config)
    end
    
    alt Checks Pass
        OSS->>GH: Green Status
        OSS->>Dev: Success Notification
    else Checks Fail
        OSS->>GH: Red Status
        OSS->>Dev: Failure Notification
    end
    
    deactivate OSS
    deactivate GH
    
    Note over Dev,OSS: Full validation happens<br/>when PR is created
```

### Diagram 4: Nightly Build on Master

```mermaid
sequenceDiagram
    participant Cron as GitHub Cron
    participant OST as openssl-tools
    participant GHP as GitHub Packages
    participant Slack as Notifications
    participant DB as Metrics DB

    Cron->>OST: Trigger nightly.yml<br/>(2 AM UTC)
    activate OST
    
    par Comprehensive Build Matrix (2-4 hours)
        OST->>OST: Linux (x86_64, ARM64)<br/>All Configs (shared/static)
        OST->>OST: Windows (x64, x86)<br/>MSVC + MinGW
        OST->>OST: macOS (Intel, Apple Silicon)
        OST->>OST: Alpine Linux (musl libc)
    end
    
    par Security & Quality
        OST->>OST: SAST (CodeQL, Semgrep)
        OST->>OST: Dependency Vuln Scan
        OST->>OST: Fuzz Testing (AFL, libFuzzer)
        OST->>OST: FIPS Compliance Tests
    end
    
    par Performance & Benchmarks
        OST->>OST: Crypto Performance Tests
        OST->>OST: Memory Leak Detection
        OST->>OST: Regression Analysis
    end
    
    OST->>GHP: Upload Nightly Artifacts
    OST->>DB: Store Metrics<br/>(build times, test results)
    
    alt All Passed
        OST->>Slack: Nightly Build Success
    else Failures Detected
        OST->>Slack: Nightly Build Failures<br/>(with AI Analysis)
        OST->>OST: Create GitHub Issue<br/>(Auto-assign maintainers)
    end
    
    deactivate OST
```

## Implementation Phases

### Phase 1: Foundation (PR #14 Merge + Basic Setup)
**Duration**: 1-2 days

1. **Merge PR #14** (CI/CD Templates)
2. **Move AI/Agent content** from PR #14 to PR #17
3. **Combine PR #15 + #16** into single PR
4. **Setup in openssl repo**:
   - Create `.github/workflows/pr-validation.yml`
   - Create `.github/workflows/lightweight-check.yml`
   - Create `.github/workflows/trigger-tools.yml`
5. **Setup in openssl-tools repo**:
   - Create `.github/workflows/pr-build.yml`
   - Create `.github/workflows/release-build.yml`
   - Create `.github/workflows/nightly.yml`
6. **Configure GitHub Secrets**:
   - `DISPATCH_TOKEN`: For cross-repo triggers
   - `PACKAGES_TOKEN`: For GitHub Packages publishing

### Phase 2: Cross-Repo Integration (repository_dispatch)
**Duration**: 2-3 days

1. **Implement triggering mechanism** in openssl workflows
2. **Implement status reporting** in openssl-tools workflows
3. **Setup GitHub Packages** repositories:
   - `staging/openssl`: For master commits
   - `production/openssl`: For tagged releases
4. **Test cross-repo communication**

### Phase 3: Artifact Management
**Duration**: 2-3 days

1. **Conan package configuration** for GitHub Packages
2. **Staging/Production separation** logic
3. **Environment protection rules** (manual approval gates)
4. **Optional**: Artifactory/GHCR fallback setup

### Phase 4: Comprehensive Testing & Nightly
**Duration**: 3-4 days

1. **Implement pyramidal test strategy**
2. **Setup nightly workflow** with full matrix
3. **Performance benchmarking** integration
4. **Security scanning** integration (CodeQL, Semgrep)

### Phase 5: AI Agent Integration (from PR #17)
**Duration**: 2-3 days

1. **Failure analysis agent** setup
2. **Auto-issue creation** with AI insights
3. **Fix suggestion** system
4. **Human review workflow**

### Phase 6: Testing & Documentation
**Duration**: 2-3 days

1. **Create test PR** in openssl repo
2. **Verify all workflows trigger correctly**
3. **Update README.md** with workflow diagrams (embed Mermaid)
4. **Cleanup temporary scripts**

## Success Criteria

- [ ] PR creation triggers fast validation + comprehensive builds
- [ ] Master merge triggers release pipeline with staging publish
- [ ] Branch commits run lightweight checks only
- [ ] Nightly builds run full matrix at 2 AM UTC
- [ ] Cross-repo communication works via repository_dispatch + Status API
- [ ] Artifacts published to GitHub Packages (staging/production)
- [ ] Manual approval gate works for production releases
- [ ] Test PR successfully exercises all workflows
- [ ] Documentation updated (README only, no new files)
- [ ] Temporary scripts cleaned up

## Repository Structure

```
sparesparrow/openssl/
├── .github/
│   └── workflows/
│       ├── pr-validation.yml          # Fast checks on PR
│       ├── lightweight-check.yml      # Branch push checks
│       ├── trigger-tools.yml          # Cross-repo trigger
│       └── basic-validation.yml       # Existing workflow (keep minimal)
├── conanfile.py                       # Minimal, delegates to tools repo
└── README.md                          # Updated with workflow diagrams

sparesparrow/openssl-tools/
├── .github/
│   └── workflows/
│       ├── pr-build.yml               # Comprehensive PR builds
│       ├── release-build.yml          # Master merge → staging
│       ├── production-deploy.yml      # Staging → production (manual)
│       ├── nightly.yml                # Full matrix + security/perf
│       └── on-demand-build.yml        # Manual trigger for testing
├── conanfile.py                       # Full build orchestration logic
├── scripts/
│   ├── publish-to-github-packages.py  # Conan → GitHub Packages
│   ├── trigger-status-update.py       # Update commit status in openssl
│   └── ai-failure-analysis.py         # AI agent integration
└── README.md                          # Updated with architecture info
```

## Cost & Performance Estimates

### GitHub Actions Minutes (Free Tier: 2000 min/month)

**Per PR** (~15 PRs/month):
- Fast validation: 5 min × 15 = 75 min
- Comprehensive builds: 45 min × 15 = 675 min
- **Total PR**: 750 min/month

**Per Master Commit** (~10 commits/month):
- Release builds: 60 min × 10 = 600 min

**Nightly Builds** (30 days/month):
- Nightly: 120 min × 30 = 3600 min → **Exceeds free tier!**

**Optimization Strategy**:
- Run nightly only 3x/week (Mon/Wed/Fri): 120 × 12 = 1440 min
- **Total**: 750 + 600 + 1440 = **2790 min/month**
- **Overage**: ~800 min × $0.008 = **$6.40/month**

**Alternative**: Use self-hosted runner for nightly builds (free)

### GitHub Packages Storage (Free Tier: 500 MB)

- Staging artifacts: ~50 MB per build × 10 = 500 MB
- **Within free tier** with cleanup policy (keep last 5)

## Next Steps

**Ready to proceed with implementation?**

I will:
1. Merge PR #14, move AI content to PR #17, combine #15+#16
2. Create workflow files in both repositories
3. Implement mermaid diagrams in README.md
4. Test with real PR in openssl repo
5. Cleanup temporary scripts

**Confirm to proceed with execution.**