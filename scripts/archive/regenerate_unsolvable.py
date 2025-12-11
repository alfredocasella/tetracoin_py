#!/usr/bin/env python3
"""
Script per rigenerare SOLO i livelli non risolvibili
Più veloce che rigenerare tutti i 300 livelli
"""

import sys
import os
import json

# Aggiungi il percorso corrente al path
# Aggiungi il percorso corrente al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Aggiungi la root del progetto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.level_loader import LevelLoader
from level_generator import create_level_data, verify_level_solvable

def regenerate_unsolvable_levels():
    """Identifica e rigenera solo i livelli non risolvibili"""
    loader = LevelLoader()
    max_levels = loader.get_level_count()
    
    print("=" * 60)
    print("RIGENERAZIONE LIVELLI NON RISOLVIBILI")
    print("=" * 60)
    print(f"Fase 1: Identificazione livelli problematici...")
    print()
    
    unsolvable = []
    
    # Fase 1: Identifica livelli non risolvibili
    for level_num in range(1, max_levels + 1):
        try:
            level = loader.load_level(level_num)
            if not verify_level_solvable(level):
                unsolvable.append(level_num)
                print(f"❌ Livello {level_num}: NON RISOLVIBILE")
        except Exception as e:
            print(f"⚠️  Livello {level_num}: Errore - {e}")
    
    if not unsolvable:
        print("\n✅ Tutti i livelli sono già risolvibili!")
        return 0
    
    print(f"\n{'=' * 60}")
    print(f"Trovati {len(unsolvable)} livelli non risolvibili")
    print(f"Livelli: {', '.join(map(str, unsolvable[:20]))}{'...' if len(unsolvable) > 20 else ''}")
    print(f"{'=' * 60}\n")
    
    # Fase 2: Rigenera solo i livelli problematici
    print(f"Fase 2: Rigenerazione {len(unsolvable)} livelli...")
    print()
    
    regenerated = 0
    failed = []
    
    for level_num in unsolvable:
        print(f"Rigenerazione livello {level_num}...", end=" ", flush=True)
        
        MAX_ATTEMPTS = 50  # Più tentativi per livelli difficili
        success = False
        
        for attempt in range(MAX_ATTEMPTS):
            try:
                # Genera nuovo livello
                level_data = create_level_data(level_num)
                
                # Verifica risolvibilità
                if verify_level_solvable(level_data, fast_mode=False):
                    # Salva livello
                    filename = f"level_{level_num:03d}.json"
                    path = os.path.join("data", "levels", filename)
                    
                    with open(path, 'w') as f:
                        json.dump(level_data, f, indent=2)
                    
                    print(f"✅ OK (tentativo {attempt + 1})")
                    regenerated += 1
                    success = True
                    break
                    
            except Exception as e:
                print(f"❌ Errore: {e}")
                break
        
        if not success:
            print(f"❌ FALLITO dopo {MAX_ATTEMPTS} tentativi")
            failed.append(level_num)
    
    # Riepilogo
    print(f"\n{'=' * 60}")
    print("RIEPILOGO RIGENERAZIONE")
    print(f"{'=' * 60}")
    print(f"✅ Livelli rigenerati con successo: {regenerated}/{len(unsolvable)}")
    
    if failed:
        print(f"❌ Livelli ancora non risolvibili: {len(failed)}")
        print(f"   Livelli: {', '.join(map(str, failed))}")
        print(f"\n💡 Suggerimento: Questi livelli potrebbero richiedere griglie più grandi")
        print(f"   o meno muri. Considera di modificare level_generator.py")
        return 1
    else:
        print(f"\n✅ TUTTI I LIVELLI SONO ORA RISOLVIBILI!")
        return 0

if __name__ == "__main__":
    sys.exit(regenerate_unsolvable_levels())
