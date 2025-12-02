#!/usr/bin/env python3
"""
Script di Test Automatizzato per TetraCoin
Esegue test automatizzabili e fornisce checklist per test manuali
"""

import sys
import os
import json
import pygame
from pathlib import Path

# Aggiungi il percorso corrente al path
# Aggiungi il percorso corrente al path (tests)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Aggiungi la root del progetto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa moduli del gioco
try:
    from core.level_loader import LevelLoader
    from core.grid_manager import GridManager
    from core.sprites import BlockSprite, CoinSprite, SHAPES
    from core.settings import *
    from core.game import Game
    from data.levels import LEVEL_DATA
except ImportError as e:
    print(f"❌ Errore importazione moduli: {e}")
    sys.exit(1)

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.results = []
        
    def test(self, test_id, description, test_func):
        """Esegue un singolo test"""
        try:
            result = test_func()
            if result:
                self.passed += 1
                status = "✅ PASS"
                print(f"{status} - {test_id}: {description}")
                self.results.append((test_id, description, "PASS", None))
            else:
                self.failed += 1
                status = "❌ FAIL"
                print(f"{status} - {test_id}: {description}")
                self.results.append((test_id, description, "FAIL", "Test returned False"))
        except Exception as e:
            self.failed += 1
            status = "❌ ERROR"
            print(f"{status} - {test_id}: {description}")
            print(f"   Errore: {e}")
            self.results.append((test_id, description, "ERROR", str(e)))
    
    def skip(self, test_id, description, reason="Test manuale"):
        """Segna un test come saltato"""
        self.skipped += 1
        status = "⏭️  SKIP"
        print(f"{status} - {test_id}: {description} ({reason})")
        self.results.append((test_id, description, "SKIP", reason))
    
    def print_summary(self):
        """Stampa il riepilogo dei test"""
        total = self.passed + self.failed + self.skipped
        print("\n" + "="*60)
        print("RIEPILOGO TEST")
        print("="*60)
        print(f"✅ Passati:  {self.passed}/{total}")
        print(f"❌ Falliti:  {self.failed}/{total}")
        print(f"⏭️  Saltati:  {self.skipped}/{total}")
        print(f"📊 Totale:   {total}")
        print("="*60)
        
        if self.failed > 0:
            print("\n⚠️  TEST FALLITI:")
            for test_id, desc, status, error in self.results:
                if status in ["FAIL", "ERROR"]:
                    print(f"  - {test_id}: {desc}")
                    if error:
                        print(f"    Errore: {error}")
        
        return self.failed == 0

def test_level_loader():
    """Test T14.1-T14.4: Caricamento livelli"""
    runner = TestRunner()
    
    loader = LevelLoader()
    
    # T14.1: Verificare che il livello 1 si carichi
    runner.test("T14.1", "Caricamento livello 1", lambda: loader.load_level(1) is not None)
    
    # T14.2: Verificare che i livelli successivi si carichino
    runner.test("T14.2", "Caricamento livello 2", lambda: loader.load_level(2) is not None)
    runner.test("T14.2", "Caricamento livello 10", lambda: loader.load_level(10) is not None)
    
    # T14.3: Verificare gestione fine livelli
    max_levels = loader.get_level_count()
    if max_levels > 0:
        runner.test("T14.3", f"Ultimo livello caricabile ({max_levels})", 
                   lambda: loader.load_level(max_levels) is not None)
        # Test che il livello successivo non esista
        try:
            loader.load_level(max_levels + 1)
            runner.test("T14.3", "Livello oltre il massimo genera errore", lambda: False)
        except FileNotFoundError:
            runner.test("T14.3", "Livello oltre il massimo genera errore", lambda: True)
    
    return runner

def test_level_data_structure():
    """Test struttura dati livello"""
    runner = TestRunner()
    loader = LevelLoader()
    
    try:
        level = loader.load_level(1)
        
        # Verifica struttura base
        runner.test("T1.1", "Livello ha grid_cols e grid_rows", 
                   lambda: 'grid_cols' in level and 'grid_rows' in level)
        runner.test("T1.1", "Livello ha layout", lambda: 'layout' in level)
        runner.test("T1.1", "Livello ha blocks", lambda: 'blocks' in level)
        runner.test("T1.1", "Livello ha coins", lambda: 'coins' in level)
        
        # Verifica dimensioni griglia
        if 'grid_cols' in level and 'grid_rows' in level:
            cols = level['grid_cols']
            rows = level['grid_rows']
            runner.test("T1.1", f"Griglia {cols}x{rows} valida", 
                       lambda: 6 <= cols <= 10 and 6 <= rows <= 10)
        
        # Verifica layout
        if 'layout' in level:
            layout = level['layout']
            runner.test("T1.1", "Layout ha numero corretto di righe", 
                       lambda: len(layout) == level.get('grid_rows', 0))
            if layout:
                runner.test("T1.1", "Layout ha numero corretto di colonne", 
                           lambda: len(layout[0]) == level.get('grid_cols', 0))
        
    except Exception as e:
        runner.test("T1.1", "Caricamento livello per test struttura", lambda: False)
        print(f"   Errore: {e}")
    
    return runner

def test_blocks_structure():
    """Test struttura blocchi"""
    runner = TestRunner()
    loader = LevelLoader()
    
    try:
        level = loader.load_level(1)
        blocks = level.get('blocks', [])
        
        if blocks:
            block = blocks[0]
            runner.test("T2.1", "Blocco ha shape", lambda: 'shape' in block)
            runner.test("T2.1", "Blocco ha color", lambda: 'color' in block)
            runner.test("T2.1", "Blocco ha start_pos o xy", 
                       lambda: 'start_pos' in block or 'xy' in block)
            runner.test("T2.1", "Blocco ha count o counter", 
                       lambda: 'count' in block or 'counter' in block)
            
            # Verifica shape valida
            if 'shape' in block:
                shape = block['shape']
                runner.test("T2.1", f"Shape {shape} è valida", 
                           lambda: shape in SHAPES)
        else:
            runner.skip("T2.1", "Nessun blocco nel livello 1")
    
    except Exception as e:
        runner.test("T2.1", "Test struttura blocchi", lambda: False)
        print(f"   Errore: {e}")
    
    return runner

def test_coins_structure():
    """Test struttura monete"""
    runner = TestRunner()
    loader = LevelLoader()
    
    try:
        level = loader.load_level(1)
        coins_data = level.get('coins', {})
        
        if isinstance(coins_data, dict):
            static_coins = coins_data.get('static', [])
            if static_coins:
                coin = static_coins[0]
                runner.test("T3.1", "Moneta ha color", lambda: 'color' in coin)
                runner.test("T3.1", "Moneta ha pos o xy", 
                           lambda: 'pos' in coin or 'xy' in coin)
            else:
                runner.skip("T3.1", "Nessuna moneta statica nel livello 1")
        else:
            # Formato vecchio
            if coins_data:
                coin = coins_data[0]
                runner.test("T3.1", "Moneta ha color", lambda: 'color' in coin)
                runner.test("T3.1", "Moneta ha pos", lambda: 'pos' in coin)
    
    except Exception as e:
        runner.test("T3.1", "Test struttura monete", lambda: False)
        print(f"   Errore: {e}")
    
    return runner

def test_game_initialization():
    """Test inizializzazione gioco"""
    runner = TestRunner()
    
    try:
        pygame.init()
        game = Game()
        
        runner.test("T26.1", "Game si inizializza correttamente", 
                   lambda: game is not None)
        runner.test("T26.1", "Game ha stato iniziale MENU", 
                   lambda: game.state == game.STATE_MENU)
        runner.test("T26.1", "Game ha level_loader", 
                   lambda: hasattr(game, 'level_loader'))
        runner.test("T26.1", "Game ha save_system", 
                   lambda: hasattr(game, 'save_system'))
        runner.test("T26.1", "Game ha audio_manager", 
                   lambda: hasattr(game, 'audio_manager'))
        runner.test("T26.1", "Game ha ui", 
                   lambda: hasattr(game, 'ui'))
        
        pygame.quit()
        
    except Exception as e:
        runner.test("T26.1", "Inizializzazione Game", lambda: False)
        print(f"   Errore: {e}")
    
    return runner

def test_level_loading():
    """Test caricamento livello nel gioco"""
    runner = TestRunner()
    
    try:
        pygame.init()
        game = Game()
        game.start_game()  # Carica livello 0 (livello 1)
        
        runner.test("T14.1", "Livello si carica nel gioco", 
                   lambda: hasattr(game, 'level_data') and game.level_data is not None)
        runner.test("T14.1", "GridManager creato", 
                   lambda: hasattr(game, 'grid_manager') and game.grid_manager is not None)
        runner.test("T14.1", "Sprite groups creati", 
                   lambda: hasattr(game, 'all_sprites') and hasattr(game, 'block_sprites'))
        runner.test("T14.1", "Stato cambia a PLAY", 
                   lambda: game.state == game.STATE_PLAY)
        runner.test("T14.1", "Timer inizializzato", 
                   lambda: hasattr(game, 'time_limit') and game.time_limit > 0)
        runner.test("T14.1", "Move count inizializzato", 
                   lambda: hasattr(game, 'move_count') and game.move_count == 0)
        runner.test("T14.1", "Level complete inizializzato", 
                   lambda: hasattr(game, 'level_complete') and not game.level_complete)
        
        pygame.quit()
        
    except Exception as e:
        runner.test("T14.1", "Caricamento livello nel gioco", lambda: False)
        print(f"   Errore: {e}")
    
    return runner

def test_victory_condition():
    """Test condizioni di vittoria"""
    runner = TestRunner()
    
    try:
        pygame.init()
        game = Game()
        game.start_game()
        
        # Simula completamento livello
        # Rimuovi tutti i blocchi e monete
        for block in list(game.block_sprites):
            block.kill()
        for coin in list(game.coin_sprites):
            coin.kill()
        game.coin_queues = []
        
        # Verifica condizione vittoria
        game.check_win_condition()
        
        runner.test("T5.1", "Level complete viene impostato", 
                   lambda: game.level_complete == True)
        runner.test("T5.4", "Stelle vengono calcolate", 
                   lambda: hasattr(game, 'stars_earned') and game.stars_earned >= 1)
        
        pygame.quit()
        
    except Exception as e:
        runner.test("T5.1", "Test condizioni vittoria", lambda: False)
        print(f"   Errore: {e}")
    
    return runner

def test_all_levels_solvable():
    """Test T22.1-T22.4: Verifica che tutti i livelli siano risolvibili"""
    runner = TestRunner()
    loader = LevelLoader()
    
    # Importa funzione di verifica dal level_generator
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))
        from level_generator import verify_level_solvable
    except ImportError:
        runner.skip("T22.1", "Impossibile importare verify_level_solvable")
        return runner
    
    max_levels = loader.get_level_count()
    
    # Test campione di livelli (per velocità)
    test_levels = [1, 5, 10, 25, 50, 75, 100, 150, 200, 250, 300]
    test_levels = [l for l in test_levels if l <= max_levels]
    
    print(f"\n🔍 Test risolvibilità su {len(test_levels)} livelli campione...")
    
    unsolvable = []
    for level_num in test_levels:
        try:
            level = loader.load_level(level_num)
            if verify_level_solvable(level):
                runner.test(f"T22.1", f"Livello {level_num} è risolvibile", lambda: True)
            else:
                unsolvable.append(level_num)
                runner.test(f"T22.1", f"Livello {level_num} è risolvibile", lambda: False)
        except Exception as e:
            runner.test(f"T22.1", f"Livello {level_num} è risolvibile", lambda: False)
            print(f"   Errore livello {level_num}: {e}")
    
    # Test completo su tutti i livelli (opzionale, più lento)
    if len(unsolvable) == 0:
        print("\n✅ Tutti i livelli campione sono risolvibili!")
        print("   Per test completo su tutti i 300 livelli, esegui: python validate_all_levels.py")
    else:
        print(f"\n⚠️  {len(unsolvable)} livelli campione potrebbero non essere risolvibili: {unsolvable}")
    
    return runner

def test_save_system():
    """Test sistema salvataggio"""
    runner = TestRunner()
    
    try:
        from core.save_system import SaveSystem
        
        save = SaveSystem()
        
        runner.test("T25.1", "SaveSystem si inizializza", 
                   lambda: save is not None)
        runner.test("T25.1", "SaveSystem ha metodo get_gold", 
                   lambda: hasattr(save, 'get_gold'))
        runner.test("T25.1", "SaveSystem ha metodo complete_level", 
                   lambda: hasattr(save, 'complete_level'))
        runner.test("T25.2", "SaveSystem può salvare stelle", 
                   lambda: hasattr(save, 'complete_level'))
        
        # Test salvataggio livello
        save.complete_level(1, 3, 10, 120.5)
        level_data = save.get_level_data(1)
        runner.test("T25.2", "Livello viene salvato", 
                   lambda: level_data is not None)
        if level_data:
            runner.test("T25.2", "Stelle vengono salvate correttamente", 
                       lambda: level_data.get('stars') == 3)
        
    except Exception as e:
        runner.test("T25.1", "Test SaveSystem", lambda: False)
        print(f"   Errore: {e}")
    
    return runner

def print_manual_tests():
    """Stampa checklist per test manuali"""
    print("\n" + "="*60)
    print("TEST MANUALI DA ESEGUIRE")
    print("="*60)
    print("\nEsegui questi test manualmente avviando il gioco:")
    print("python main.py\n")
    
    manual_tests = [
        ("T2.2-T2.8", "Sistema Blocchi: Verifica visualizzazione contatori, drag & drop, collisioni, scomparsa"),
        ("T3.2-T3.5", "Sistema Monete: Verifica raccolta, decremento contatore, colori"),
        ("T4.1-T4.5", "Sistema Movimento: Verifica mouse, tastiera, click, contatore mosse"),
        ("T5.2-T5.5", "Condizioni Vittoria: Verifica schermata, stelle, statistiche"),
        ("T6.1-T6.4", "Condizioni Sconfitta: Verifica timer, schermata, vite"),
        ("T7.1-T7.5", "Sistema Timer: Verifica countdown, colori, stati"),
        ("T8.1-T8.4", "Sistema Obiettivi: Verifica visualizzazione, aggiornamenti, checkmark"),
        ("T9.1-T9.5", "HUD Superiore: Verifica layout, posizionamento, visibilità"),
        ("T10.1-T10.4", "Pannello Obiettivi: Verifica posizionamento, scaling"),
        ("T11.1-T11.3", "Barra Inferiore: Verifica posizionamento, pulsante Reset"),
        ("T12.1-T12.5", "Schermata Vittoria: Verifica layout, stelle, statistiche, istruzioni"),
        ("T13.1-T13.4", "Schermata Sconfitta: Verifica layout, informazioni"),
        ("T15.1-T15.4", "Transizione Vittoria: Verifica cambio livello, reset stato"),
        ("T16.1-T16.3", "Transizione Sconfitta: Verifica riprova, menu"),
        ("T17.1-T17.4", "Audio SFX: Verifica suoni movimento, raccolta, vittoria, sconfitta"),
        ("T18.1-T18.2", "Audio Musica: Verifica musica di sottofondo"),
        ("T19.1-T19.2", "Prestazioni: Verifica FPS"),
        ("T20.1-T20.2", "Memoria: Verifica utilizzo memoria"),
        ("T21.1-T21.4", "Edge Cases: Verifica casi limite"),
        ("T22.1-T22.4", "Robustezza: Verifica gestione errori"),
    ]
    
    for test_ids, description in manual_tests:
        print(f"⏭️  {test_ids}: {description}")
    
    print("\n" + "="*60)

def main():
    """Esegue tutti i test"""
    print("="*60)
    print("TEST AUTOMATIZZATI - TETRACOIN")
    print("="*60)
    print()
    
    all_passed = True
    
    # Test caricamento livelli
    print("\n📦 TEST CARICAMENTO LIVELLI (T14.1-T14.4)")
    print("-" * 60)
    runner = test_level_loader()
    all_passed = all_passed and (runner.failed == 0)
    
    # Test struttura dati
    print("\n📊 TEST STRUTTURA DATI LIVELLO (T1.1)")
    print("-" * 60)
    runner = test_level_data_structure()
    all_passed = all_passed and (runner.failed == 0)
    
    # Test struttura blocchi
    print("\n🧱 TEST STRUTTURA BLOCCHI (T2.1)")
    print("-" * 60)
    runner = test_blocks_structure()
    all_passed = all_passed and (runner.failed == 0)
    
    # Test struttura monete
    print("\n🪙 TEST STRUTTURA MONETE (T3.1)")
    print("-" * 60)
    runner = test_coins_structure()
    all_passed = all_passed and (runner.failed == 0)
    
    # Test inizializzazione gioco
    print("\n🎮 TEST INIZIALIZZAZIONE GIOCO (T26.1)")
    print("-" * 60)
    runner = test_game_initialization()
    all_passed = all_passed and (runner.failed == 0)
    
    # Test caricamento livello
    print("\n📥 TEST CARICAMENTO LIVELLO NEL GIOCO (T14.1)")
    print("-" * 60)
    runner = test_level_loading()
    all_passed = all_passed and (runner.failed == 0)
    
    # Test condizioni vittoria
    print("\n🏆 TEST CONDIZIONI VITTORIA (T5.1, T5.4)")
    print("-" * 60)
    runner = test_victory_condition()
    all_passed = all_passed and (runner.failed == 0)
    
    # Test sistema salvataggio
    print("\n💾 TEST SISTEMA SALVATAGGIO (T25.1-T25.2)")
    print("-" * 60)
    runner = test_save_system()
    all_passed = all_passed and (runner.failed == 0)
    
    # Test risolvibilità livelli
    print("\n🔍 TEST RISOLVIBILITÀ LIVELLI (T22.1-T22.4)")
    print("-" * 60)
    runner = test_all_levels_solvable()
    all_passed = all_passed and (runner.failed == 0)
    
    # Riepilogo
    print("\n" + "="*60)
    print("RIEPILOGO FINALE")
    print("="*60)
    
    if all_passed:
        print("✅ Tutti i test automatizzati sono passati!")
    else:
        print("⚠️  Alcuni test automatizzati sono falliti. Controlla i dettagli sopra.")
    
    # Stampa test manuali
    print_manual_tests()
    
    print("\n💡 SUGGERIMENTO: Esegui i test manuali avviando il gioco e seguendo la checklist.")
    print("   Documenta i risultati nel file TEST_PLAN.md\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

