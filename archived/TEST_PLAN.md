# Piano di Test - TetraCoin

## 1. Test Funzionalità Core

### 1.1 Sistema di Griglia
- [ ] **T1.1**: Verificare che la griglia venga renderizzata correttamente (6x6, 7x7, 8x8)
- [ ] **T1.2**: Verificare che le celle vuote, muri e void siano visualizzati correttamente
- [ ] **T1.3**: Verificare che la griglia sia centrata correttamente nello schermo
- [ ] **T1.4**: Verificare che la griglia non vada fuori schermo su diverse risoluzioni

### 1.2 Sistema Blocchi
- [ ] **T2.1**: Verificare che tutti i blocchi vengano posizionati correttamente all'inizio del livello
- [ ] **T2.2**: Verificare che i blocchi mostrino il contatore corretto
- [ ] **T2.3**: Verificare che i blocchi possano essere trascinati fluidamente
- [ ] **T2.4**: Verificare che il fantasma verde/rosso appaia durante il drag
- [ ] **T2.5**: Verificare che i blocchi si aggancino correttamente alla griglia al rilascio
- [ ] **T2.6**: Verificare che i blocchi non possano essere posizionati su muri
- [ ] **T2.7**: Verificare che i blocchi non possano sovrapporsi ad altri blocchi
- [ ] **T2.8**: Verificare che i blocchi scompaiano quando il contatore raggiunge 0

### 1.3 Sistema Monete
- [ ] **T3.1**: Verificare che le monete vengano posizionate correttamente
- [ ] **T3.2**: Verificare che le monete vengano raccolte quando un blocco del colore corrispondente le copre
- [ ] **T3.3**: Verificare che il contatore del blocco decrementi quando una moneta viene raccolta
- [ ] **T3.4**: Verificare che più monete possano essere raccolte in un singolo movimento
- [ ] **T3.5**: Verificare che le monete non vengano raccolte se il colore non corrisponde

### 1.4 Sistema Movimento
- [ ] **T4.1**: Verificare movimento con mouse (drag & drop)
- [ ] **T4.2**: Verificare movimento con tastiera (frecce)
- [ ] **T4.3**: Verificare movimento con click su cella adiacente
- [ ] **T4.4**: Verificare che il contatore mosse si aggiorni correttamente
- [ ] **T4.5**: Verificare che movimenti non validi vengano rifiutati

## 2. Test Sistema di Gioco

### 2.1 Condizioni di Vittoria
- [ ] **T5.1**: Verificare che il livello si completi quando tutti i blocchi sono scomparsi
- [ ] **T5.2**: Verificare che il livello si completi quando tutte le monete sono state raccolte
- [ ] **T5.3**: Verificare che il livello si completi solo se il timer non è scaduto
- [ ] **T5.4**: Verificare che la schermata di vittoria appaia correttamente
- [ ] **T5.5**: Verificare che le stelle vengano calcolate correttamente in base alle mosse

### 2.2 Condizioni di Sconfitta
- [ ] **T6.1**: Verificare che il livello fallisca quando il timer raggiunge 0
- [ ] **T6.2**: Verificare che la schermata di sconfitta appaia correttamente
- [ ] **T6.3**: Verificare che una vita venga persa quando il timer scade
- [ ] **T6.4**: Verificare che il pulsante "Riprova" funzioni correttamente

### 2.3 Sistema Timer
- [ ] **T7.1**: Verificare che il timer parta correttamente all'inizio del livello
- [ ] **T7.2**: Verificare che il timer decrementi correttamente
- [ ] **T7.3**: Verificare che il timer cambi colore in stato WARNING (50%)
- [ ] **T7.4**: Verificare che il timer cambi colore e pulsante in stato CRITICAL (20%)
- [ ] **T7.5**: Verificare che il timer si fermi quando il livello è completato

### 2.4 Sistema Obiettivi
- [ ] **T8.1**: Verificare che gli obiettivi vengano visualizzati correttamente
- [ ] **T8.2**: Verificare che il contatore "raccolte/richieste" si aggiorni in tempo reale
- [ ] **T8.3**: Verificare che il checkmark appaia quando un obiettivo è completato
- [ ] **T8.4**: Verificare che gli obiettivi siano calcolati correttamente dai contatori dei blocchi

## 3. Test UI e Layout

### 3.1 HUD Superiore
- [ ] **T9.1**: Verificare che il badge mondo/livello sia visibile e non sovrapposto
- [ ] **T9.2**: Verificare che il testo del livello non vada fuori schermo
- [ ] **T9.3**: Verificare che il timer pillola sia centrato e visibile
- [ ] **T9.4**: Verificare che vite e oro siano posizionati correttamente (se c'è spazio)
- [ ] **T9.5**: Verificare che il pulsante pausa sia sempre visibile e cliccabile

### 3.2 Pannello Obiettivi
- [ ] **T10.1**: Verificare che il pannello obiettivi sia posizionato correttamente
- [ ] **T10.2**: Verificare che le pillole obiettivi non vadano fuori schermo
- [ ] **T10.3**: Verificare che le pillole si scalino se necessario
- [ ] **T10.4**: Verificare che il pannello non si sovrapponga alla griglia o alla barra inferiore

### 3.3 Barra Inferiore
- [ ] **T11.1**: Verificare che la barra inferiore sia sempre in fondo allo schermo
- [ ] **T11.2**: Verificare che il pulsante Reset sia visibile e centrato
- [ ] **T11.3**: Verificare che il pulsante Reset funzioni correttamente

### 3.4 Schermata Vittoria
- [ ] **T12.1**: Verificare che la card di vittoria sia centrata e visibile
- [ ] **T12.2**: Verificare che le stelle vengano visualizzate correttamente
- [ ] **T12.3**: Verificare che le statistiche siano corrette
- [ ] **T12.4**: Verificare che la card non vada fuori schermo
- [ ] **T12.5**: Verificare che l'istruzione "Premi un tasto" sia visibile

### 3.5 Schermata Sconfitta
- [ ] **T13.1**: Verificare che la card di sconfitta sia centrata e visibile
- [ ] **T13.2**: Verificare che il motivo del fallimento sia mostrato
- [ ] **T13.3**: Verificare che le vite rimanenti siano mostrate
- [ ] **T13.4**: Verificare che le istruzioni siano visibili

## 4. Test Transizioni e Flusso

### 4.1 Caricamento Livelli
- [ ] **T14.1**: Verificare che il livello 1 si carichi correttamente
- [ ] **T14.2**: Verificare che i livelli successivi si carichino correttamente
- [ ] **T14.3**: Verificare che il gioco gestisca correttamente la fine dei livelli disponibili
- [ ] **T14.4**: Verificare che il gioco ritorni al menu quando non ci sono più livelli

### 4.2 Transizione Vittoria → Livello Successivo
- [ ] **T15.1**: Verificare che premendo un tasto nella schermata vittoria si carichi il livello successivo
- [ ] **T15.2**: Verificare che cliccando nella schermata vittoria si carichi il livello successivo
- [ ] **T15.3**: Verificare che lo stato del gioco venga resettato correttamente
- [ ] **T15.4**: Verificare che il nuovo livello parta con timer, mosse e obiettivi corretti

### 4.3 Transizione Sconfitta → Riprova
- [ ] **T16.1**: Verificare che premendo R nella schermata sconfitta si ricarichi il livello
- [ ] **T16.2**: Verificare che premendo ESC nella schermata sconfitta si torni al menu
- [ ] **T16.3**: Verificare che il livello si ricarichi correttamente

## 5. Test Audio

### 5.1 Effetti Sonori
- [ ] **T17.1**: Verificare che il suono di movimento venga riprodotto
- [ ] **T17.2**: Verificare che il suono di raccolta moneta venga riprodotto
- [ ] **T17.3**: Verificare che il suono di vittoria venga riprodotto
- [ ] **T17.4**: Verificare che il suono di sconfitta venga riprodotto

### 5.2 Musica
- [ ] **T18.1**: Verificare che la musica di sottofondo parta all'avvio
- [ ] **T18.2**: Verificare che la musica continui durante il gioco

## 6. Test Prestazioni

### 6.1 Frame Rate
- [ ] **T19.1**: Verificare che il gioco mantenga 60 FPS su dispositivi mid-range
- [ ] **T19.2**: Verificare che il gioco mantenga almeno 30 FPS su dispositivi low-end

### 6.2 Memoria
- [ ] **T20.1**: Verificare che l'utilizzo di memoria non superi 200MB
- [ ] **T20.2**: Verificare che non ci siano memory leak durante sessioni lunghe

## 7. Test Edge Cases

### 7.1 Casi Limite
- [ ] **T21.1**: Verificare comportamento con griglia completamente piena di muri
- [ ] **T21.2**: Verificare comportamento con un solo blocco e una sola moneta
- [ ] **T21.3**: Verificare comportamento con blocchi che occupano tutta la griglia
- [ ] **T21.4**: Verificare comportamento quando si raccolgono tutte le monete in un solo movimento

### 7.2 Errori e Robustezza
- [ ] **T22.1**: Verificare che tutti i livelli siano risolvibili (ogni blocco può raggiungere le sue monete)
- [ ] **T22.2**: Verificare che il gioco non crashi se un livello JSON è corrotto
- [ ] **T22.3**: Verificare che il gioco gestisca correttamente livelli mancanti
- [ ] **T22.4**: Verificare che il gioco gestisca correttamente input rapidi multipli
- [ ] **T22.5**: Verificare che il gioco gestisca correttamente resize finestra (se supportato)

## 8. Test Compatibilità

### 8.1 Risoluzioni Schermo
- [ ] **T23.1**: Test su risoluzione 540x960 (target)
- [ ] **T23.2**: Test su risoluzioni più piccole (se supportate)
- [ ] **T23.3**: Test su risoluzioni più grandi (se supportate)

### 8.2 Sistemi Operativi
- [ ] **T24.1**: Test su macOS
- [ ] **T24.2**: Test su Linux
- [ ] **T24.3**: Test su Windows (se disponibile)

## 9. Test Salvataggio

### 9.1 Sistema Salvataggio
- [ ] **T25.1**: Verificare che il progresso venga salvato dopo ogni livello completato
- [ ] **T25.2**: Verificare che le stelle vengano salvate correttamente
- [ ] **T25.3**: Verificare che l'oro venga salvato correttamente
- [ ] **T25.4**: Verificare che i livelli sbloccati vengano salvati correttamente

## 10. Checklist Pre-Rilascio

### 10.1 Funzionalità Obbligatorie
- [ ] **T26.1**: Tutte le funzionalità core sono implementate e funzionanti
- [ ] **T26.2**: UI completa e conforme al GDD
- [ ] **T26.3**: Sistema di livelli funzionante (almeno 10-15 livelli)
- [ ] **T26.4**: Sistema di vittoria/sconfitta funzionante
- [ ] **T26.5**: Sistema timer funzionante

### 10.2 Qualità
- [ ] **T27.1**: Nessun bug critico
- [ ] **T27.2**: Nessun crash durante gameplay normale
- [ ] **T27.3**: Performance accettabili
- [ ] **T27.4**: UI responsive e senza sovrapposizioni

## Note per i Tester

1. **Priorità Alta**: Test T15.1, T15.2, T15.3 (transizione vittoria → livello successivo) - **PROBLEMA CRITICO ATTUALE**
2. **Priorità Alta**: Test T9.1-T9.5, T10.1-T10.4, T12.1-T12.5 (layout UI) - **PROBLEMA GRAFICO ATTUALE**
3. **Priorità Media**: Tutti gli altri test funzionali
4. **Priorità Bassa**: Test di performance e compatibilità

## Come Segnalare Bug

Per ogni bug trovato, includere:
- Numero del test fallito (es. T15.1)
- Descrizione del problema
- Passi per riprodurre
- Screenshot (se applicabile)
- Sistema operativo e risoluzione schermo

