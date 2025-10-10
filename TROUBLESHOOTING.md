# 🔧 Troubleshooting Guide - OpenSSL Build System

## Často Řešené Problémy

### 1. "Is a directory" chyba při ./config

**Problém:** `./config: Is a directory`

**Příčina:** Nesprávný pracovní adresář, spouštění ./config mimo kořen OpenSSL zdrojů.

**Řešení:**
```yaml
- name: Build step
  working-directory: openssl-source  # ✅ Správně
  run: ./config --options
```

### 2. Conan profil chyby

**Problém:** `ERROR: The default build profile doesn't exist`

**Příčina:** Chybí default profil v CI prostředí.

**Řešení:**
```bash
# Vždy před conan install
conan profile detect --force

# Nebo explicitní profily
conan install . --profile:host=myprofile --profile:build=myprofile
```

### 3. CMake flagy v OpenSSL Configure

**Problém:** `-DCMAKE_C_COMPILER=gcc` v `./config` volání

**Příčina:** OpenSSL nepoužívá CMake, má vlastní Configure systém.

**Řešení:**
```bash
# ❌ Nesprávně
./config -DCMAKE_C_COMPILER=gcc

# ✅ Správně  
export CC=gcc
./config
```

### 4. Windows PowerShell problémy

**Problém:** `rm -rf` nefunguje na Windows

**Řešení:**
```yaml
- name: Remove files (Cross-platform)
  shell: bash
  run: |
    if [[ "${{ runner.os }}" == "Windows" ]]; then
      powershell -Command "Remove-Item -Recurse -Force path"
    else
      rm -rf path
    fi
```

### 5. Pomalé CI buildy

**Řešení:**
- Používejte Conan cache s `actions/cache@v4`
- Nastavte `fail-fast: false` jen když nutné
- Využijte path filters pro omezení běhů
- Minimalizujte matrix kombinace

## Rychlé Opravy

### Reset Conan prostředí
```bash
conan profile detect --force
conan remove "*" --confirm
```

### Debug workflow krok
```yaml
- name: Debug info
  run: |
    echo "OS: ${{ runner.os }}"
    echo "Workspace: ${{ github.workspace }}"
    pwd
    ls -la
```

### Test lokální Conan setup
```bash
cd openssl-crypto
conan create . --build=missing -v
```
