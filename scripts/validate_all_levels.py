#!/usr/bin/env python3
"""
Script per validare la risolvibilità di TUTTI i livelli
Esegue un controllo completo su tutti i 300 livelli
"""

import sys
import os

# Aggiungi il percorso corrente al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Aggiungi la root del progetto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.level_loader import LevelLoader
from level_generator import verify_level_solvable

def main():
    loader = LevelLoader()
    max_levels = loader.get_level_count()
    
    print("=" * 60)
    print("VALIDAZIONE COMPLETA RISOLVIBILITÀ LIVELLI")
    print("=" * 60)
    print(f"Verifica di {max_levels} livelli...")
    print()
    
    unsolvable = []
    errors = []
    
    for level_num in range(1, max_levels + 1):
        try:
            level = loader.load_level(level_num)
            
            if verify_level_solvable(level):
                if level_num % 50 == 0:
                    print(f"✓ Livello {level_num}/{max_levels}...")
            else:
                unsolvable.append(level_num)
                print(f"❌ Livello {level_num}: NON RISOLVIBILE")
                
        except Exception as e:
            errors.append((level_num, str(e)))
            print(f"❌ Livello {level_num}: ERRORE - {e}")
    
    print("\n" + "=" * 60)
    print("RIEPILOGO")
    print("=" * 60)
    print(f"✅ Livelli risolvibili: {max_levels - len(unsolvable) - len(errors)}/{max_levels}")
    
    if unsolvable:
        print(f"❌ Livelli NON risolvibili: {len(unsolvable)}")
        print(f"   Livelli: {', '.join(map(str, unsolvable[:20]))}{'...' if len(unsolvable) > 20 else ''}")
        print(f"\n💡 Suggerimento: Rigenera i livelli non risolvibili con:")
        print(f"   python scripts/level_generator.py")
    
    if errors:
        print(f"⚠️  Errori di caricamento: {len(errors)}")
        for level_num, error in errors[:5]:
            print(f"   Livello {level_num}: {error}")
    
    if not unsolvable and not errors:
        print("✅ TUTTI I LIVELLI SONO RISOLVIBILI!")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())

