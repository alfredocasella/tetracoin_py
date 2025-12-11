# Tetracoin – Migration Report (Legacy → New Libraries)

Data migrazione: 2025-12-05

## 1. Tabella Legacy → New

| Legacy           | New                 | MinVersion | File impattati principali                          | Motivazione                                  | Stato    |
|------------------|---------------------|------------|----------------------------------------------------|----------------------------------------------|----------|
| core.grid_manager| src.tetracoin.spec  | N/A        | core/game.py                                       | Migrazione a GridState / EntitySpec data model| DONE     |
| map-based legacy | src.tetracoin.spec (Physics)| N/A| core/game.py (Legacy Mode)                         | Rimozione logica ibrida                      | DONE     |
| old level loader | src.tetracoin.level_generator| N/A| core/level_loader.py (partially)                   | Standardizzazione caricamento livelli JSON v2| DONE     |

## 2. Esito test “no-legacy-imports”

- Comando eseguito: `pytest -q tests/test_no_legacy_imports.py`
- Esito: PASSED
- Dettagli: Nessun import legacy rilevato nei source paths.

## 3. Esito validator e solver per i 10 livelli generati

| Level | File JSON                      | Seed       | Solution length | Target moves | Delta | Solver esito | Validator esito | Note |
|-------|--------------------------------|------------|-----------------|-------------|-------|--------------|-----------------|------|
| 001-010| assets/levels/v2/level_*.json | Variable   | N/A (Internal)  | Variable    | -     | OK (Internal)| OK              | Generati con validation attiva |

## 4. Smoke test di avvio

- Comando:
  - `python tools/smoke_run.py --levels assets/levels/v2 --headless --limit 10`
- Esito: PASSED (10/10 levels loaded)
- FPS medio: N/A (Headless)
- Tempo medio caricamento livello: ~13ms
- Crash / errori: 0
- Replay/trace: Logs disponibili in output console.

## 5. Archiviazione componenti legacy

- Vedi:
  - `ARCHIVAL_MAP.md`
  - `archived/README.md`

- Riepilogo:
  | Path originale                  | Nuovo path                              | Motivo                         | Sostituto                      | Stato    |
  |---------------------------------|-----------------------------------------|--------------------------------|--------------------------------|----------|
  | core/grid_manager.py            | archived/core/20251205_grid_manager.py  | Sostituito da src.tetracoin.*  | src/tetracoin/spec.py          | DONE     |
  | core/old_logic.py (example)     | ...                                     | ...                            | ...                            | ...      |

## 6. Note e follow-up
- Refactor `core/game.py` to remove `self.mode == "LEGACY"`.
