#!/usr/bin/env python3
"""
Visual Level Test - Verifica grafica e logica dei livelli
Controlla:
- Conteggio obiettivi corretto
- Monete non sovrapposte a blocchi
- Monete dentro i confini della griglia
- Risolvibilità BFS
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from level_loader import LevelLoader
from level_generator import verify_level_solvable, SHAPE_CELLS

def test_level_visual(level_num):
    """Test visuale completo di un livello"""
    loader = LevelLoader()
    
    try:
        level = loader.load_level(level_num)
    except Exception as e:
        return {"level": level_num, "status": "ERROR", "errors": [f"Load failed: {e}"]}
    
    errors = []
    warnings = []
    
    # 1. Check grid bounds
    grid_w, grid_h = level['meta']['grid_size']
    layout = level['layout']
    
    # 2. Check blocks
    blocks = level['blocks']
    all_block_cells = set()
    
    for block in blocks:
        shape = block['shape']
        pos = block['xy']
        shape_cells = SHAPE_CELLS.get(shape, [(0, 0)])
        
        for dx, dy in shape_cells:
            cell_x = pos[0] + dx
            cell_y = pos[1] + dy
            
            # Check bounds
            if not (0 <= cell_x < grid_w and 0 <= cell_y < grid_h):
                errors.append(f"Block {block['id']} extends outside grid at ({cell_x}, {cell_y})")
            
            all_block_cells.add((cell_x, cell_y))
    
    # 3. Check coins
    coins = level['coins']['static']
    coin_positions = set()
    coin_counts_by_color = {}
    
    for coin in coins:
        pos = tuple(coin['xy'])
        color = coin['color']
        
        # Check bounds
        if not (0 <= pos[0] < grid_w and 0 <= pos[1] < grid_h):
            errors.append(f"Coin at {pos} is outside grid bounds")
        
        # Check overlap with blocks
        if pos in all_block_cells:
            errors.append(f"Coin at {pos} overlaps with block")
        
        # Check duplicates
        if pos in coin_positions:
            warnings.append(f"Duplicate coin at {pos}")
        coin_positions.add(pos)
        
        # Count by color
        coin_counts_by_color[color] = coin_counts_by_color.get(color, 0) + 1
    
    # 4. Check objective counts match
    for block in blocks:
        color = block['color']
        required = block['counter']
        available = coin_counts_by_color.get(color, 0)
        
        if available != required:
            errors.append(f"Block {block['id']} ({color}) needs {required} coins but has {available} available")
    
    # 5. Check solvability
    if not verify_level_solvable(level, fast_mode=False):
        errors.append("Level is NOT SOLVABLE (BFS check failed)")
    
    # Determine status
    if errors:
        status = "FAIL"
    elif warnings:
        status = "WARN"
    else:
        status = "PASS"
    
    return {
        "level": level_num,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "blocks": len(blocks),
        "coins": len(coins)
    }

def main():
    print("=" * 60)
    print("VISUAL LEVEL TEST - Livelli 1-20")
    print("=" * 60)
    print()
    
    results = []
    for level_num in range(1, 21):
        result = test_level_visual(level_num)
        results.append(result)
        
        status_icon = "✓" if result['status'] == "PASS" else ("⚠" if result['status'] == "WARN" else "✗")
        print(f"{status_icon} Livello {level_num:2d}: {result['status']:4s} ({result['blocks']} blocchi, {result['coins']} monete)")
        
        for error in result['errors']:
            print(f"    ERROR: {error}")
        for warning in result['warnings']:
            print(f"    WARN: {warning}")
    
    print()
    print("=" * 60)
    print("RIEPILOGO")
    print("=" * 60)
    
    pass_count = sum(1 for r in results if r['status'] == 'PASS')
    warn_count = sum(1 for r in results if r['status'] == 'WARN')
    fail_count = sum(1 for r in results if r['status'] == 'FAIL')
    
    print(f"✅ PASS: {pass_count}/20")
    print(f"⚠️  WARN: {warn_count}/20")
    print(f"❌ FAIL: {fail_count}/20")
    
    if fail_count == 0:
        print("\n✅ Tutti i livelli 1-20 sono corretti!")
        return 0
    else:
        print(f"\n❌ {fail_count} livelli hanno errori critici")
        return 1

if __name__ == "__main__":
    sys.exit(main())
