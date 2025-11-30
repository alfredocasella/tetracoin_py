

Ecco il **Game Design Document (GDD) v4.0 - Complete Python Edition**.

-----

# TetraCoin – Master Game Design Document

**Versione:** 2.0 (Python Architecture)
**Target:** 300 Livelli (Mobile, Desktop, Web)
**Tecnologia:** Python 3.12+, Pygame CE, Pygbag (Web), Buildozer (Android)

-----

## 1\. High Concept & Visione

**Sintesi:**
Un puzzle game logico "zen-ma-teso". Il giocatore trascina blocchi (Tetramini) su una griglia per raccogliere monete colorate. Ogni blocco ha un **"Contatore Vita"** che diminuisce raccogliendo monete; a zero, il blocco scompare (implode).
La sfida è l'ordine di esecuzione: liberare spazio al momento giusto per permettere l'ingresso di nuove monete o il passaggio di altri blocchi.

**Piattaforme:**

1.  **Desktop (Dev/Release):** Windows/Mac/Linux (Nativo).
2.  **Web (WASM):** Via `pygbag` (per demo e viralità immediata senza installazione).
3.  **Mobile (Android):** Via `Buildozer`/`Kivy` (target finale con controlli touch).

-----

## 2\. Architettura Tecnica (Python Modulare)

Per gestire 300 livelli, il codice deve separare nettamente *Logica* da *Rendering*.

### 2.1 Struttura del File System

```text
TetraCoin/
├── main.py                 # Entry point (Bootstrap)
├── assets/                 # Sprite, Font, SFX, Musica
├── data/
│   ├── levels/             # 300 file JSON (es. world1_001.json)
│   ├── player_save.json    # Progresso, Stelle, Valuta
│   └── config.json         # Impostazioni (Audio, Lingua)
└── src/
    ├── core/
    │   ├── app.py          # Gestione finestra e Game Loop principale
    │   ├── asset_manager.py# Cache per immagini/suoni (Flyweight pattern)
    │   ├── event_bus.py    # Sistema Pub/Sub per eventi (es. on_coin_collected)
    │   └── save_system.py  # Gestione persistenza dati
    ├── logic/
    │   ├── grid.py         # Matrice logica, pathfinding semplice
    │   ├── level_parser.py # Caricatore JSON
    │   └── validator.py    # Regole di movimento (Snap, Collisioni)
    ├── entities/
    │   ├── block.py        # Logica del Tetramino (Counter, Shape)
    │   └── props.py        # Coins, Walls, Doors, Switch
    ├── scenes/
    │   ├── menu_scene.py
    │   ├── game_scene.py   # Il cuore del gameplay
    │   └── editor_scene.py # STRUMENTO CRITICO: Level Editor integrato
    └── ui/
        └── hud.py          # Timer, Stelle, Bottoni
```

### 2.2 Formato Dati Livello (Esteso)

Il JSON deve supportare le meccaniche avanzate dei mondi futuri.

```json
{
  "meta": {
    "id": 105,
    "world": 1,
    "name": "The Narrow Path",
    "difficulty": "Easy",
    "grid_size": [8, 8],        // Larghezza, Altezza
    "time_limit": 180,          // Secondi
    "stars": [10, 14, 20]       // Mosse max per 3, 2, 1 stella
  },
  "layout": [                   // 0=Empty, 1=Wall, 9=Void, 2=NeutralBlock
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 2, 1],
    ...
  ],
  "blocks": [
    { "id": "b1", "shape": "T4", "color": "blue", "counter": 3, "xy": [2, 3] },
    { "id": "b2", "shape": "I2", "color": "red",  "counter": 5, "xy": [5, 5] }
  ],
  "coins": {
    "static": [
       { "color": "blue", "xy": [1, 1] }
    ],
    "entrances": [
       { "xy": [4, 0], "queue": ["red", "red", "blue", "green"] }
    ]
  },
  "mechanics": {
    "teleporters": [ { "in": [2,2], "out": [6,6] } ],
    "switches":    [ { "pos": [3,3], "target_door": [3,4] } ]
  }
}
```

-----

## 3\. Core Gameplay Loop

### 3.1 Movimento & Snap (Fluidità)

  * **Input:** Mouse (Desktop) o Touch (Mobile).
  * **Visual Feedback:** Mentre trascini, il blocco è semitrasparente. Un "Fantasma" (Ghost) verde/rosso appare sulla griglia per indicare dove atterrerà (Snap Preview).
  * **Regola del Ritorno:** Se il rilascio avviene in posizione invalida (sovrapposizione, fuori griglia), il blocco torna alla posizione di partenza con un'animazione elastica (`Lerp`).

### 3.2 La Meccanica del Contatore (Cuore del Gioco)

Ogni blocco ha un numero stampato sopra (es. **3**).

1.  Il blocco si muove sopra una moneta del suo colore.
2.  **Effetto:** Moneta raccolta (+1 valuta, particelle).
3.  **Logica:** Contatore del blocco scende a **2**.
4.  **Zero:** Quando il contatore tocca **0**, il blocco emette un suono, "implode" e **sparisce dalla griglia**.
      * *Design Note:* Questo libera spazio cruciale per manovrare altri blocchi ingombranti.

### 3.3 Il "Paradosso dello Spawn" (Code di Monete)

Le **Coin Queue Entrances** sono celle speciali da cui escono monete in fila indiana.

  * **Regola Standard:** Raccogli la moneta in cima -\> Appare subito quella dopo.
  * **Il Paradosso (Edge Case):** Se un blocco si ferma sopra l'entrata per raccogliere la moneta, occupa fisicamente la cella. La moneta successiva **non può spawnare** finché il blocco non si sposta.
      * *Eccezione "Vorace":* Se la moneta in arrivo nella coda è dello **stesso colore** del blocco che sta occupando l'entrata, il blocco la "mangia" istantaneamente senza doversi muovere, scalando il contatore. Questo permette combo velocissime.

-----

## 4\. Progressione: I 300 Livelli

Per arrivare a 300 livelli senza annoiare, dividiamo il gioco in **5 Mondi** da 60 livelli ciascuno, introducendo una meccanica ogni 15-20 livelli.

### Mondo 1: The Factory (Tutorial & Basi)

  * **Livelli 1-10:** Solo monete statiche, griglie 6x6. Forme semplici (I2, I3, O4).
  * **Livelli 11-30:** Introduzione del "Contatore" che fa sparire i blocchi. Muri semplici.
  * **Livelli 31-60:** Introduzione delle **Code di Monete**. Gestione dello spazio.

### Mondo 2: Quantum Lab (Teletrasporto)

  * **Meccanica:** Celle **Teleporter**. Entri in A, esci in B.
  * **Twist:** I blocchi grandi (es. L4) possono esistere "a metà" tra due portali se non c'è spazio sufficiente dall'altra parte? *Decisione semplificata per Phase 1:* Un blocco passa solo se c'è spazio completo dall'altra parte.

### Mondo 3: Logic Gates (Porte & Switch)

  * **Meccanica:** Celle **Switch** (a pressione). Se un blocco ci sta sopra, una **Porta** (muro colorato) si apre (diventa pavimento). Appena ti sposti, si chiude.
  * **Puzzle:** Usare un blocco "sacrificale" o neutrale per tenere aperto il passaggio per un altro.

### Mondo 4: Flow City (Direzioni)

  * **Meccanica:** Celle **One-Way** (nastri trasportatori). Puoi trascinare un blocco sopra queste celle solo nella direzione della freccia.
  * **Twist:** Blocchi che devono fare "giri immensi" per raggiungere una moneta vicina.

### Mondo 5: The Mastermind (Mix Totale)

  * Combinazione di tutte le meccaniche. Griglie 10x10.
  * Introduzione dei "Blocchi Maledetti": Se il timer scade, esplodono e fanno Game Over istantaneo (aumentano la tensione).

-----

## 5\. Meta-Game & Monetizzazione (Simulata/Reale)

### 5.1 Sistema a Stelle (Stars)

Basato sulle mosse (non sul tempo, per premiare la logica).

  * **3 Stelle:** Risolto nel numero minimo di mosse (o quasi).
  * **2 Stelle:** \< 1.5x mosse minime.
  * **1 Stella:** Completato in qualsiasi numero di mosse.
  * *Il tempo è solo una condizione di sconfitta (Fail State), non di punteggio.*

### 5.2 Valuta Soft (TetraGold)

  * Guadagni: 10 gold per livello finito, +5 per ogni stella.
  * Spese: Power-up, Skip Level, Skin per i blocchi.

### 5.3 Power-up (Acquistabili con TetraGold)

Per aiutare l'utente nei livelli difficili (evita l'abbandono):

1.  **Hammer (Martello):** Distrugge un blocco istantaneamente (utile se hai sbagliato i calcoli e un blocco inutile ostruisce).
2.  **Magnet (Magnete):** Attira tutte le monete di un colore specifico verso i blocchi corrispondenti (non consuma mosse).
3.  **Time Freeze:** Aggiunge 60 secondi al timer.

-----

## 6\. UI & UX (Adattiva)

L'interfaccia deve scalare da Monitor 16:9 a Smartphone 9:16.

  * **Top Bar:**
      * SX: Tasto Pausa.
      * Centro: Timer (Pillola bianca, diventa rossa sotto i 20s).
      * DX: Contatore Vite (Cuori) e Valuta.
  * **Grid Area:**
      * Centrata verticalmente.
      * Sfondo griglia leggermente più scuro dello sfondo app.
  * **Bottom Area:**
      * **Objective Panel:** Mostra quali colori mancano (es. "Rosso: 2/5", "Blu: 0/3").
      * **Toolbar:** Tasti Power-up e Tasto "Undo" (Annulla ultima mossa - Costa 0, limitato a 3 per livello o infinito? *Consiglio: Infinito ma invalida le 3 stelle se abusato*).

-----

## 7\. Roadmap Sviluppo & Strategia "300 Livelli"

Il problema principale non è il codice, è il **Content Design**. Scrivere 300 JSON a mano è follia.

### Fase 1: Il Core & L'Editor (Settimane 1-3)

  * Implementare Grid, Block Logic, Counter e Win/Lose.
  * **Cruciale:** Creare un `editor_scene.py` in-game.
      * Premi 'E' nel menu -\> Apre una griglia vuota.
      * Click sx: Piazza Muro. Click dx: Piazza Moneta. Tasti 1-5: Seleziona forma blocco.
      * Tasto 'S': Salva JSON nella cartella `/data/levels`.
      * *Questo ti permetterà di creare un livello in 2 minuti invece che in 20.*

### Fase 2: Tutorial & Mondo 1 (Settimane 4-5)

  * Creare i primi 20 livelli per raffinare la difficoltà.
  * Implementare UI completa (HUD, Victory Screen).
  * Aggiungere Audio.

### Fase 3: Expansion & Build (Settimane 6-8)

  * Implementare meccaniche Mondo 2 e 3.
  * Usare l'editor per generare i livelli 21-100.
  * Setup di **Pygbag** per build Web (testabile subito su itch.io).

### Fase 4: Polish & Mobile (Settimane 9+)

  * Integrazione Save System (File locale).
  * Setup **Buildozer** per creare l'APK Android.
  * Implementazione Ads (tramite bridge Python-Java o servizi fake per versione desktop).

-----

## 8\. Note Tecniche per Python

**Fail Fast & Deadlock Detection:**
In Python, possiamo implementare un controllo leggero in background:

```python
def check_deadlock(grid, blocks):
    # Se non ci sono monete e counter > 0 -> Perso
    # Se ci sono monete ma nessun blocco può muoversi -> Perso
    # Algoritmo: Per ogni blocco, prova a muoverlo in 4 direzioni (virtualmente).
    # Se moves_possible == 0: trigger_game_over("No moves left!")
```

Questo evita che il giocatore fissi lo schermo per 2 minuti quando il livello è matematicamente irrisolvibile.

**Gestione Risoluzione:**
Usa un sistema di *Virtual Resolution*. Disegna tutto su una surface 1080x1920 (Portrait target) e poi scala l'immagine finale in base alla finestra dell'utente (`pygame.transform.smoothscale`).

-----

### Prossimo Passo che posso fare per te

Vuoi che generi il codice per **`editor_scene.py`**?
Avere l'editor funzionante subito è l'unico modo per garantirti di riuscire a produrre 300 livelli in tempi ragionevoli. Posso scriverti uno script Pygame che ti permette di disegnare i livelli col mouse e salvarli in quel formato JSON.