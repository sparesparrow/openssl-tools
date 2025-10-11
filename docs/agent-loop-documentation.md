# Agent-Loop.sh - Kompletní dokumentace

## Přehled
Robustní CI orchestrace s plánováním a validací pomocí Cursor-Agent pro OpenSSL modernizaci. Tento skript kombinuje tradiční CI operace s AI-asistovaným plánováním pro automatizovanou opravu GitHub workflows.

## Základní použití

### Dva hlavní režimy:

**Planning Mode** - Analýza a tvorba plánu:
```bash
./agent-loop.sh "Diagnostika a plán pro PR #6" planning
```

**Execution Mode** - Validace a provádění:
```bash
./agent-loop.sh "Oprav všechny selhané workflows" execution
```

## Konfigurace prostředí

### Základní parametry:
- `PR_NUMBER=6` - Číslo pull requestu
- `PR_BRANCH=simplify-openssl-build` - Název větve PR
- `REPO=sparesparrow/openssl-tools` - Repository
- `MAX_ITERATIONS=12` - Maximum iterací
- `INTERVAL=60` - Interval mezi iteracemi (sekundy)

### Cursor-Agent konfigurace (POVINNÉ pro AI funkce):
- `CURSOR_API_KEY` - **POVINNÉ** - API klíč z cursor.com/settings/api
- `AGENT_TIMEOUT_SEC=600` - Timeout pro agent (sekundy)
- `CURSOR_CONFIG_FILE=.cursor/cli-config.json` - Cesta ke konfiguraci Cursor
- `CURSOR_MCP_CONFIG=mcp.json` - MCP konfigurace pro pokročilé funkce
- `CURSOR_AGENT_CONFIG=.cursor/agents/ci-repair-agent.yml` - Specifická agent konfigurace

### Pokročilé nastavení:
- `LOG_LEVEL=info` - Úroveň logování (debug|info|warn|error)
- `USE_STREAMING=false` - Streaming režim pro real-time sledování progress
- `AGENT_MODEL=auto` - Model pro AI agent (auto vybere nejlepší dostupný)
- `MCP_ENABLED=true` - Zapnout MCP podporu pro přístup k dodatečným nástrojům

## Nastavení Cursor API klíče

### Získání API klíče:
1. Jděte na [cursor.com/settings/api](https://cursor.com/settings/api)
2. Přihlaste se k vašemu Cursor účtu
3. Klikněte "Create new API key"
4. Zkopírujte klíč (zobrazí se pouze jednou!)

### Nastavení v prostředí:
```bash
export CURSOR_API_KEY="your-api-key-here"
```

### Ověření konfigurace:
```bash
# Ověřte instalaci cursor-agent
cursor-agent --version

# Test připojení
echo "Test connection" | cursor-agent -p
```

## Instalace cursor-agent CLI

### Automatická instalace:
```bash
curl https://cursor.com/install -fsS | bash
```

### Manuální nastavení PATH:
```bash
# Pro bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Pro zsh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc  
source ~/.zshrc
```

### Ověření instalace:
```bash
cursor-agent --version
```

## Model Context Protocol (MCP) konfigurace

### Co je MCP:
MCP je otevřený standard pro připojení AI aplikací k externím systémům a datům. Umožňuje AI agentům přístup k:
- Workflow historie a analýze
- Repository struktuře a metadatům  
- Build logs a error analýze
- GitHub API funkcím

### Základní MCP konfigurace (`mcp.json`):
```json
{
  "mcpServers": {
    "github": {
      "command": "mcp-server-github",
      "args": ["--token", "your-github-token"]
    },
    "filesystem": {
      "command": "mcp-server-filesystem", 
      "args": ["--root", "."]
    }
  }
}
```

### Pokročilá konfigurace (`.cursor/cli-config.json`):
```json
{
  "model": "claude-3.5-sonnet",
  "timeout": 600000,
  "mcp": {
    "enabled": true,
    "servers": ["github", "filesystem"]
  }
}
```

## Příklady použití

### 1. Základní oprava CI pro PR #6:
```bash
export CURSOR_API_KEY="sk-..."
./agent-loop.sh "Ensure all PR #6 workflows are green with minimal changes" execution
```

### 2. Detailní analýza s debug logováním:
```bash
export LOG_LEVEL=debug
export CURSOR_API_KEY="sk-..."
./agent-loop.sh "Analyze failed Conan 2.0 workflows and create repair plan" planning
```

### 3. Streaming mode pro real-time sledování:
```bash
export USE_STREAMING=true
export CURSOR_API_KEY="sk-..."
./agent-loop.sh "Fix OpenSSL modernization compatibility issues" execution
```

### 4. Specifické workflow opravy:
```bash
export PR_NUMBER=6
export PR_BRANCH=simplify-openssl-build
./agent-loop.sh "Fix binary-first-ci.yml and conan-ci-enhanced.yml failures" execution
```

## Automatické akce které skript provádí

### GitHub workflow operace:
- **rerun:ID** - Znovu spustit selhané workflow run
- **approve:ID** - Schválit workflow vyžadující manual approval  
- **apply-patch:filename** - Aplikovat unified diff patch na soubor
- **enable-workflow:path** - Přesunout workflow z workflows-disabled/ do workflows/
- **disable-workflow:path** - Přesunout workflow z workflows/ do workflows-disabled/
- **rerun-failed-workflows** - Znovu spustit všechny aktuálně selhané workflow runs

### AI plánování a validace:
- Analýza selhání workflows a jejich příčin
- Tvorba minimálních, bezpečných YAML patchů
- Prioritizace akcí (approve > rerun > patch)
- Validace YAML syntaxe před aplikací
- Kontrola rizik a kompatibility s Conan 2.0

### Git operace:
- Automatické commitování změn s popisnými commit zprávami
- Push do PR větve s retry logikou
- Branch management a checkout

## Výstupní JSON formáty

### Plán z Planning Mode:
```json
{
  "batches": [
    {
      "name": "batch-1-rerun-failed",
      "actions": [
        "rerun:12345", 
        "approve:67890",
        "apply-patch:workflow-fix.yml"
      ]
    }
  ],
  "patches": [
    {
      "filename": ".github/workflows/conan-ci-enhanced.yml",
      "diff": "--- a/.github/workflows/conan-ci-enhanced.yml\n+++ b/.github/workflows/conan-ci-enhanced.yml\n@@ -10,1 +10,1 @@\n-    branches: [main]\n+    branches: [main, simplify-openssl-build]"
    }
  ],
  "stop_condition": "all_green",
  "notes": "Added PR branch to workflow triggers for proper CI execution"
}
```

### Validace z Execution Mode:
```json
{
  "valid": true,
  "issues": [],
  "corrected_patches": [],
  "recommendations": [
    "Add concurrency group to prevent job cancellation",
    "Consider workflow caching for faster builds"
  ]
}
```

## Požadavky na systém

### Povinné nástroje:
- `gh` (GitHub CLI) - pro GitHub API operace
- `jq` (JSON processor) - pro zpracování JSON odpovědí  
- `git` - pro repository operace
- `curl` - pro HTTP requesty
- `timeout` - pro řízení timeoutů
- `cursor-agent` (volitelné) - pro AI funkce

### Přístupová práva:
- GitHub personal access token s repository přístupem
- Cursor API key pro AI funkcionalitu  
- Write přístup k target repository (sparesparrow/openssl-tools)

### Ověření GitHub CLI:
```bash
# Přihlášení
gh auth login

# Test přístupu k repository
gh repo view sparesparrow/openssl-tools

# Test workflow operací
gh run list --repo sparesparrow/openssl-tools --limit 5
```

## Troubleshooting a řešení problémů

### Časté chyby a řešení:

**"CURSOR_API_KEY not set":**
```bash
# Získejte klíč z cursor.com/settings/api
export CURSOR_API_KEY="your-key-from-cursor-settings"
```

**"cursor-agent command not found":**
```bash
# Instalace cursor-agent
curl https://cursor.com/install -fsS | bash
# Pak restartujte terminal nebo:
source ~/.bashrc  # nebo ~/.zshrc
```

**"JSON parsing errors from agent":**
```bash
# Debug mode pro detailní logy
export LOG_LEVEL=debug
./agent-loop.sh "task" execution 2>&1 | tee debug.log
```

**"Permission denied" při git operacích:**
```bash
# Ověřte GitHub autentizaci
gh auth status
# Zkontrolujte SSH klíče
ssh -T git@github.com
```

**"No workflow runs found":**
```bash
# Zkontrolujte že jste na správné větvi
git branch
git checkout simplify-openssl-build
# Ověřte PR existenci
gh pr view 6
```

### Debug režim a logging:

**Zapnutí debug logování:**
```bash
export LOG_LEVEL=debug
./agent-loop.sh "task" execution 2>&1 | tee -a agent-debug.log
```

**Analýza logů:**
```bash
# Filtrování error zpráv
grep '"level":"error"' agent-debug.log | jq '.'

# Sledování agent komunikace
grep '"level":"debug"' agent-debug.log | grep -i agent | jq '.msg'
```

### Performance optimalizace:

**Rychlé iterace:**
```bash
export MAX_ITERATIONS=5
export INTERVAL=30
```

**Streaming pro real-time feedback:**
```bash
export USE_STREAMING=true
```

**Timeout konfigurace:**
```bash
export AGENT_TIMEOUT_SEC=300  # Pro rychlejší response
```

## Pokročilé použití

### Custom agent konfigurace (`.cursor/agents/ci-repair-agent.yml`):
```yaml
name: ci-repair-agent
description: Specialized agent for CI/CD workflow repairs
model: claude-3.5-sonnet
temperature: 0.1
max_tokens: 4000
system_prompt: |
  You are a CI/CD expert specializing in GitHub Actions and OpenSSL build systems.
  Focus on minimal, safe changes that preserve functionality while fixing failures.
```

### Batch processing více PR:
```bash
for pr in 5 6 7; do
  export PR_NUMBER=$pr
  ./agent-loop.sh "Fix PR #$pr workflows" execution
  sleep 60
done
```

### Integration s CI/CD pipeline:
```bash
# V GitHub Actions workflow
- name: Run agent-loop
  run: |
    export CURSOR_API_KEY="${{ secrets.CURSOR_API_KEY }}"
    ./agent-loop.sh "Automated CI repair" execution
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## MCP (Model Context Protocol) Integration

### Overview
MCP je otevřený standard pro připojení AI aplikací k externím systémům a datům. V kontextu `agent-loop.sh` umožňuje:

- **Automatické připojení** k MCP serverům
- **Přístup k nástrojům** z více serverů současně
- **Implementace vzorů** z [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- **Podpora workflow pause/resume** signálů

### MCP Server Flow
```
User->>Client: Send query
Client<<->>MCP_Server: Get available tools
Client->>Claude: Send query with tool descriptions
Claude-->>Client: Decide tool execution
Client->>MCP_Server: Request tool execution
MCP_Server->>Tools: Execute chosen tools
Tools-->>MCP_Server: Return results
MCP_Server-->>Client: Send results
Client->>Claude: Send tool results
Claude-->>Client: Provide final response
Client-->>User: Display response
```

### MCP Best Practices

1. **Error Handling**
   - Využijte type system pro explicitní modelování chyb
   - Zabalte externí volání do `try-catch` bloků
   - Poskytujte jasné a smysluplné chybové zprávy
   - Řešte network timeouts a connection issues

2. **Security**
   - Ukládejte API klíče bezpečně v `local.properties`, environment variables, nebo secret managers
   - Validujte všechny externí odpovědi
   - Buďte opatrní s permissions a trust boundaries

### MCP Troubleshooting

**Server Path Issues:**
```bash
# Relative path
java -jar build/libs/client.jar ./server/build/libs/server.jar

# Absolute path
java -jar build/libs/client.jar /Users/username/projects/mcp-server/build/libs/server.jar

# Windows path
java -jar build/libs/client.jar C:/projects/mcp-server/build/libs/server.jar
```

**Response Timing:**
- První odpověď může trvat až 30 sekund
- To je normální během inicializace serveru
- Následující odpovědi jsou typicky rychlejší
- Nepřerušujte proces během počátečního čekání

**Common Error Messages:**
- `Connection refused`: Ujistěte se, že server běží a cesta je správná
- `Tool execution failed`: Ověřte, že jsou nastaveny požadované environment variables
- `ANTHROPIC_API_KEY is not set`: Zkontrolujte environment variables

## Architektura a design

### Hlavní komponenty:

1. **Configuration Management** - Načítání a validace konfigurace
2. **Cursor Agent Integration** - AI-powered plánování a validace
3. **GitHub API Operations** - Workflow management a monitoring
4. **JSON Processing** - Robustní zpracování AI odpovědí
5. **Error Handling** - Graceful fallback a recovery
6. **Logging System** - Strukturované logování s různými úrovněmi

### Design Patterns:

- **Strategy Pattern** - Různé režimy (planning vs execution)
- **Template Method** - Standardizovaný workflow pro všechny operace
- **Observer Pattern** - Real-time monitoring workflow statusu
- **Command Pattern** - Batch execution akcí
- **Factory Pattern** - Dynamické vytváření prompts a konfigurací

Tento skript představuje pokročilý nástroj pro automatizaci CI/CD operací s využitím moderních AI technologií pro inteligentní rozhodování a opravu workflows.
