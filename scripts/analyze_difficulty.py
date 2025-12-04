#!/usr/bin/env python3
"""
Script per analizzare e visualizzare la curva di difficoltà dei livelli
"""

import sys
import os

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'scripts'))

from level_generator_v3 import DifficultyProgression

def analyze_difficulty():
    """Analizza e stampa la curva di difficoltà"""
    
    difficulty = DifficultyProgression()
    
    # Livelli chiave da analizzare
    key_levels = [1, 5, 10, 15, 20, 30, 50, 75, 100, 120, 150, 200, 250, 300]
    
    print("=" * 80)
    print("ANALISI CURVA DI DIFFICOLTÀ")
    print("=" * 80)
    print()
    
    print(f"{'Livello':<10} {'Blocchi':<10} {'Monete/B':<10} {'Griglia':<12} {'Muri%':<10} {'Mosse Target':<15}")
    print("-" * 80)
    
    for level in key_levels:
        target = difficulty.get_target_difficulty(level)
        grid = f"{target['grid'][0]}x{target['grid'][1]}"
        walls = f"{target['walls']*100:.1f}%"
        moves = f"{target['target_moves'][0]}-{target['target_moves'][1]}"
        
        print(f"{level:<10} {target['blocks']:<10} {target['coins_per_block']:<10} {grid:<12} {walls:<10} {moves:<15}")
    
    print()
    print("=" * 80)
    print("CONFRONTO DIFFICOLTÀ")
    print("=" * 80)
    print()
    
    # Confronto livelli 10-20 vs 100-120
    print("📊 Livelli 10-20 (Facili):")
    for level in range(10, 21):
        target = difficulty.get_target_difficulty(level)
        print(f"  Livello {level}: {target['blocks']} blocchi, {target['coins_per_block']} monete/blocco, {target['target_moves'][0]}-{target['target_moves'][1]} mosse")
    
    print()
    print("📊 Livelli 100-120 (Difficili):")
    for level in range(100, 121, 5):
        target = difficulty.get_target_difficulty(level)
        print(f"  Livello {level}: {target['blocks']} blocchi, {target['coins_per_block']} monete/blocco, {target['target_moves'][0]}-{target['target_moves'][1]} mosse")
    
    print()
    print("=" * 80)
    print("METRICHE COMPARATIVE")
    print("=" * 80)
    print()
    
    # Calcola metriche medie
    avg_10_20_blocks = sum(difficulty.get_target_difficulty(i)['blocks'] for i in range(10, 21)) / 11
    avg_10_20_coins = sum(difficulty.get_target_difficulty(i)['coins_per_block'] for i in range(10, 21)) / 11
    avg_10_20_moves = sum(difficulty.get_target_difficulty(i)['target_moves'][1] for i in range(10, 21)) / 11
    
    avg_100_120_blocks = sum(difficulty.get_target_difficulty(i)['blocks'] for i in range(100, 121)) / 21
    avg_100_120_coins = sum(difficulty.get_target_difficulty(i)['coins_per_block'] for i in range(100, 121)) / 21
    avg_100_120_moves = sum(difficulty.get_target_difficulty(i)['target_moves'][1] for i in range(100, 121)) / 21
    
    print(f"Media Livelli 10-20:")
    print(f"  • Blocchi: {avg_10_20_blocks:.1f}")
    print(f"  • Monete/blocco: {avg_10_20_coins:.1f}")
    print(f"  • Mosse max: {avg_10_20_moves:.1f}")
    print()
    
    print(f"Media Livelli 100-120:")
    print(f"  • Blocchi: {avg_100_120_blocks:.1f}")
    print(f"  • Monete/blocco: {avg_100_120_coins:.1f}")
    print(f"  • Mosse max: {avg_100_120_moves:.1f}")
    print()
    
    print(f"Rapporto di difficoltà (100-120 / 10-20):")
    print(f"  • Blocchi: {avg_100_120_blocks / avg_10_20_blocks:.2f}x")
    print(f"  • Monete/blocco: {avg_100_120_coins / avg_10_20_coins:.2f}x")
    print(f"  • Mosse max: {avg_100_120_moves / avg_10_20_moves:.2f}x")
    print()

if __name__ == "__main__":
    analyze_difficulty()
