# TetraCoin - Pygame Game

Un gioco puzzle in stile Tetris realizzato con Pygame. Contiene 300+ livelli generati proceduralmente.

## Build Android

Questo progetto utilizza **GitHub Actions** per compilare automaticamente l'APK Android.

### Come scaricare l'APK compilato:

1. Vai su: https://github.com/alfredocasella/tetracoin_py/actions
2. Seleziona l'ultima build completata
3. Scarica l'artifact `tetracoin-debug.apk`

---

# Guideline

1. Copia:
   bash
   cp -R ~/Developer/project-template ~/Developer/Personali/sito-portfolio
   cd ~/Developer/Personali/sito-portfolio
   

2. Decidi che **tipo** di progetto è:
   - Se è solo React:
     - Usi `frontend/`
     - Puoi cancellare `backend/` e magari `src/` se non lo usi
   - Se è API backend puro:
     - Usi `backend/`
     - Puoi cancellare `frontend/`
   - Se è CLI o libreria:
     - Usi `src/`
     - Puoi cancellare `backend/` e `frontend/`

3. Mantieni sempre:
   - `tests/` (prima o poi ti servirà)
   - `scripts/` (anche solo per 1–2 script)
   - `.vscode/` (impostazioni progetto)

---


# Nome del Progetto

> Breve descrizione del progetto.

## Struttura

- `backend/` – Backend del progetto (API, servizi, logica di business)
- `frontend/` – Frontend (web, React, ecc.)
- `src/` – Codice principale se il progetto è monoblocco
- `tests/` – Test automatici
- `docs/` – Documentazione
- `scripts/` – Script di supporto (build, deploy, manutenzione)
- `.vscode/` – Configurazioni specifiche per l'editor

## Requisiti

- [ ] Linguaggio/stack principale:
- [ ] Versione:
- [ ] Dipendenze principali:

## Setup rapido

```bash
# Clona il repository
git clone <url>

# Entra nella cartella
cd <nome-progetto>

# Comandi di setup (da definire)

#### `.gitignore`

Un `.gitignore` “universale” per Mac, Python, Node/React, .NET, Xcode (lo userai poi come base per i progetti reali):

```bash
cat > .gitignore << 'EOF'
# macOS
.DS_Store
.AppleDouble
.LSOverride

# Thumbnails
._*

# Node / JavaScript / TypeScript
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
dist/
build/
.cache/
.next/
out/

# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.pkl
*.pyo
*.pyd
*.pyo
*.egg-info/
.eggs/
*.egg
.env
.venv
venv/
ENV/
env/
.mypy_cache/
.pytest_cache/
.coverage
coverage.xml
htmlcov/

# C# / .NET
bin/
obj/
*.user
*.suo
*.userosscache
*.sln.docstates

# VS Code
.vscode/*
!.vscode/settings.json
!.vscode/launch.json
!.vscode/extensions.json

# Logs
logs/
*.log

# IDE varie
.idea/
*.iml

# Xcode / iOS
DerivedData/
build/
*.xcuserstate
xcuserdata/

# Misc
*.swp
*.swo
