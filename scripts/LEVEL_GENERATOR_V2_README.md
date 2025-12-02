# Level Generator V2 - Guida d'Uso

## Panoramica

Il Level Generator V2 è conforme al GDD 4.0 e genera livelli con:
- ✅ Curva di difficoltà progressiva
- ✅ Validazione rigorosa con solver BFS/A*
- ✅ Livello 1 hardcoded come tutorial
- ✅ Minimo 4 blocchi dal livello 4 in poi
- ✅ Generazione sequenziale con bilanciamento automatico

## Utilizzo

### Generare Tutti i 300 Livelli

```bash
python scripts/level_generator_v2.py --generate-all
```

⚠️ **ATTENZIONE**: Questo comando cancellerà TUTTI i livelli esistenti in `data/levels/` prima di generare i nuovi.

### Generare un Numero Specifico di Livelli

```bash
# Genera i primi 20 livelli
python scripts/level_generator_v2.py --num-levels 20

# Genera livelli 51-100
python scripts/level_generator_v2.py --start-from 51 --num-levels 100
```

### Rigenerare Solo Alcuni Livelli

```bash
# Rigenera livelli 10-20 (senza cancellare gli altri)
python scripts/level_generator_v2.py --start-from 10 --num-levels 20
```

## Curva di Difficoltà

### Livelli 1-10 (Tutorial e Introduzione)
- **L1**: 1 blocco, 2 monete, 6x6, 0% muri (HARDCODED)
- **L2-3**: 1-2 blocchi, 2-3 monete, 6x6, 0% muri
- **L4-10**: 4+ blocchi, 3-4 monete, 6x7, 0-5% muri

### Livelli 11-50 (Progressione Base)
- 4-5 blocchi, 3-4 monete, 7x8, 5-8% muri

### Livelli 51-150 (Intermedio)
- 4-5 blocchi, 4-5 monete, 8x9, 8-12% muri

### Livelli 151-250 (Avanzato)
- 5-6 blocchi, 4-5 monete, 9x10, 10-15% muri

### Livelli 251-300 (Esperto)
- 6 blocchi, 5 monete, 10x10, 12-15% muri

## Validazione

Ogni livello generato viene validato per:

1. **Struttura**: Presenza di tutti i campi richiesti
2. **Risolvibilità**: Verificato con solver BFS/A*
3. **Complessità Minima**: Almeno 5 mosse richieste
4. **Raggiungibilità Monete**: Tutte le monete devono essere raggiungibili
5. **No Sovrapposizioni**: Blocchi e monete non si sovrappongono

## Workflow Completo

### 1. Generazione

```bash
# Genera tutti i 300 livelli
python scripts/level_generator_v2.py --generate-all
```

### 2. Validazione

```bash
# Valida tutti i livelli generati
python scripts/validate_all_levels.py
```

### 3. Test

```bash
# Esegui test suite
python tests/run_tests.py
```

### 4. Test Manuale

```bash
# Testa il gioco
python main.py
```

## Troubleshooting

### Livelli Non Risolvibili

Se alcuni livelli risultano non risolvibili dopo la generazione:

```bash
# Rigenera solo i livelli problematici
python scripts/regenerate_unsolvable.py
```

### Performance Lenta

La generazione può richiedere tempo (2-4 ore per 300 livelli). Per velocizzare:

1. Genera in batch più piccoli
2. Riduci `max_attempts` nel codice (default: 100)
3. Usa un computer più potente

### Livelli Troppo Facili/Difficili

Modifica i parametri in `DifficultyProgression._build_difficulty_curve()`:
- `blocks`: Numero di blocchi
- `coins_per_block`: Monete per blocco
- `grid`: Dimensione griglia
- `walls`: Densità muri (0.0-0.15)
- `target_moves`: Range mosse target

## File Generati

Ogni livello viene salvato come `data/levels/level_XXX.json` con formato:

```json
{
  "meta": {
    "id": 1,
    "world": 1,
    "name": "Level 1",
    "grid_size": [6, 6],
    "time_limit": 120,
    "stars": [2, 3, 5]
  },
  "layout": [[0, 0, ...], ...],
  "blocks": [...],
  "coins": {
    "static": [...],
    "entrances": []
  }
}
```

## Confronto con Generatore Vecchio

| Feature | Vecchio | V2 |
|---------|---------|-----|
| Validazione | Parziale | Rigorosa (BFS/A*) |
| Difficoltà | Casuale | Progressiva |
| Tutorial | No | Sì (L1 hardcoded) |
| Min Blocchi L4+ | No | Sì (min 4) |
| Bilanciamento | No | Automatico |
| Generazione | Batch | Sequenziale |

## Note Importanti

⚠️ **Hard Delete**: Il generatore cancella TUTTI i livelli esistenti prima di generare i nuovi. Fai un backup se necessario!

✅ **GDD 4.0 Compliant**: Tutti i requisiti del GDD 4.0 sono implementati.

📊 **Statistiche**: Il generatore mostra statistiche dettagliate al termine della generazione.
