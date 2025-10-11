
## 🎯 Operační Postupy pro Vývojáře

### CI/CD Workflow Přehled

#### Hlavní Workflows
- **`multi-platform-build.yml`** - Produkční multi-platform buildy
- **`security-scan.yml`** - Bezpečnostní skenování a compliance
- **Override workflows** - Dočasné kompatibilní vrstvy

#### Pro Vývojáře
```bash
# Lokální test před push
conan create openssl-crypto/ --build=missing
conan create openssl-ssl/ --build=missing  
conan create openssl-tools/ --build=missing

# CI se spustí automaticky na:
git push origin feature-branch  # → PR workflow
git push origin main           # → Plný build + upload
```

#### Pro Release Inženýry
```bash
# Kontrola bezpečnosti před release
gh run list --workflow=security-scan.yml
gh run download [run-id] --pattern security-reports

# Manuální spuštění CI
gh workflow run multi-platform-build.yml

# Upload artefaktů
gh release upload v1.0.0 sbom-cyclonedx.json
```

### Monitoring a Metriky

- **Build časy:** Sledovat přes GitHub Actions insights
- **Cache hit rate:** Conan cache metriky v lozích
- **Security alerts:** Automatické přes Dependabot + CodeQL
- **SBOM tracking:** Artefakty u každého releaseu
