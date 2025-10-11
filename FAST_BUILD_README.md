# ⚡ FAST BUILD & UPLOAD - READY TO GO!

## 🚀 **IMMEDIATE BUILD COMMANDS**

### **Option 1: Super Quick Start (Recommended)**
```bash
# One command setup and build
./scripts/quick-start.sh setup
./scripts/quick-start.sh build
```

### **Option 2: Maximum Speed Build**
```bash
# Set credentials and build immediately
export ARTIFACTORY_URL="https://your-artifactory.com"
export ARTIFACTORY_TOKEN="your-token"
./scripts/build-all-platforms-now.sh
```

### **Option 3: Fast Build Pipeline**
```bash
# Full pipeline with all optimizations
export ARTIFACTORY_URL="https://your-artifactory.com"
export ARTIFACTORY_TOKEN="your-token"
./scripts/super-fast-build.sh
```

## ⚡ **SPEED OPTIMIZATIONS**

### **Parallel Builds**
- **All platforms build simultaneously**
- **Uses all CPU cores** (`nproc` parallel builds)
- **10-minute timeout per platform**
- **Docker BuildKit enabled**

### **Docker Optimizations**
- **Multi-stage builds** with minimal final images
- **Build cache** for faster rebuilds
- **ccache** for C/C++ compilation speed
- **Optimized base images** with pre-installed dependencies

### **Build Matrix**
- ✅ **Ubuntu 20.04** (GCC 11)
- ✅ **Ubuntu 22.04** (Clang 14)  
- ✅ **Windows 2022** (MSVC 193)
- ✅ **macOS x86_64** (Apple Clang 14)
- ✅ **macOS ARM64** (Apple Clang 14)

## 🔧 **QUICK SETUP**

### **1. Set Credentials**
```bash
# Option A: Environment variables
export ARTIFACTORY_URL="https://your-artifactory.com"
export ARTIFACTORY_TOKEN="your-token"
export ARTIFACTORY_REPO="openssl-releases"

# Option B: Quick setup script
./scripts/quick-start.sh setup
```

### **2. Build All Platforms**
```bash
# Maximum speed build
./scripts/build-all-platforms-now.sh
```

### **3. Check Results**
```bash
# View artifacts
ls -la artifacts/*.tar.gz

# Check Artifactory
# Visit: https://your-artifactory.com/artifactory/openssl-releases/
```

## 📊 **EXPECTED PERFORMANCE**

### **Build Times**
- **Single platform**: 5-10 minutes
- **All platforms parallel**: 10-15 minutes
- **Total pipeline**: 15-20 minutes

### **Artifact Sizes**
- **Ubuntu builds**: ~50-100MB each
- **Windows builds**: ~100-200MB each
- **macOS builds**: ~50-100MB each
- **Total artifacts**: ~500MB-1GB

### **Upload Speed**
- **Parallel uploads**: All artifacts upload simultaneously
- **Upload time**: 2-5 minutes (depending on connection)
- **Total time**: 20-25 minutes end-to-end

## 🛠️ **BUILD SCRIPTS COMPARISON**

| Script | Speed | Features | Use Case |
|--------|-------|----------|----------|
| `build-all-platforms-now.sh` | ⚡⚡⚡ | Maximum speed, minimal features | **FASTEST BUILD** |
| `super-fast-build.sh` | ⚡⚡ | Fast with optimizations | **BALANCED** |
| `fast-build-and-upload.sh` | ⚡ | Full pipeline with monitoring | **COMPLETE** |
| `quick-start.sh` | ⚡⚡ | Interactive setup + build | **EASY START** |

## 🚀 **IMMEDIATE EXECUTION**

### **For Maximum Speed:**
```bash
# Set credentials
export ARTIFACTORY_URL="https://your-artifactory.com"
export ARTIFACTORY_TOKEN="your-token"

# Build everything NOW
./scripts/build-all-platforms-now.sh
```

### **For Easy Setup:**
```bash
# Interactive setup
./scripts/quick-start.sh setup
./scripts/quick-start.sh build
```

## 📋 **REQUIREMENTS**

### **System Requirements**
- **Docker** (running)
- **curl** (for uploads)
- **git** (for version detection)
- **bash** (for scripts)

### **Credentials Required**
- **Artifactory URL** (e.g., `https://your-company.jfrog.io`)
- **Artifactory Token** (API key or password)
- **Repository Name** (default: `openssl-releases`)

## 🔍 **TROUBLESHOOTING**

### **Common Issues**

**Docker not running:**
```bash
sudo systemctl start docker
```

**Missing credentials:**
```bash
export ARTIFACTORY_URL="your-url"
export ARTIFACTORY_TOKEN="your-token"
```

**Build timeout:**
```bash
export BUILD_TIMEOUT=1200  # 20 minutes
./scripts/build-all-platforms-now.sh
```

**Out of memory:**
```bash
export MAX_PARALLEL=2  # Reduce parallel builds
./scripts/build-all-platforms-now.sh
```

### **Check Build Logs**
```bash
# View build logs
ls -la logs/build-*.log

# Check specific platform
tail -f logs/build-ubuntu-22.04-clang.log
```

## 📦 **ARTIFACT STRUCTURE**

### **Generated Artifacts**
```
artifacts/
├── openssl-20241201-abc123-ubuntu-20.04-gcc.tar.gz
├── openssl-20241201-abc123-ubuntu-22.04-clang.tar.gz
├── openssl-20241201-abc123-windows-2022.tar.gz
├── openssl-20241201-abc123-macos-x86_64.tar.gz
└── openssl-20241201-abc123-macos-arm64.tar.gz
```

### **Artifact Contents**
Each archive contains:
- **OpenSSL binaries** (`openssl`, `libssl.so`, `libcrypto.so`)
- **Headers** (`openssl/` directory)
- **Libraries** (`lib/` directory)
- **Build metadata** (`BUILD_INFO.json`)
- **Checksums** (`SHA256SUMS`)

## 🎯 **SUCCESS CRITERIA**

### **Build Success**
- ✅ All 5 platforms built successfully
- ✅ Artifacts created and packaged
- ✅ Uploaded to Artifactory
- ✅ Total time < 25 minutes

### **Verification**
```bash
# Check artifacts
ls -la artifacts/*.tar.gz

# Verify uploads
curl -H "Authorization: Bearer $ARTIFACTORY_TOKEN" \
  "$ARTIFACTORY_URL/artifactory/openssl-releases/"

# Test artifact download
curl -H "Authorization: Bearer $ARTIFACTORY_TOKEN" \
  -o test.tar.gz \
  "$ARTIFACTORY_URL/artifactory/openssl-releases/openssl-20241201-abc123-ubuntu-22.04-clang.tar.gz"
```

## 🚀 **READY TO BUILD!**

**Choose your speed:**

1. **MAXIMUM SPEED**: `./scripts/build-all-platforms-now.sh`
2. **EASY START**: `./scripts/quick-start.sh setup`
3. **BALANCED**: `./scripts/super-fast-build.sh`

**All platforms will be built and uploaded in 15-25 minutes!** ⚡