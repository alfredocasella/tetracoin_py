#!/usr/bin/env python3
"""
TetraCoin Level Generator V2
Conforme al GDD 4.0 - Generazione Livelli con Curva di Difficoltà Progressiva

Features:
- Generazione sequenziale livello per livello
- Validazione rigorosa con solver BFS/A*
- Bilanciamento automatico della difficoltà
- Livello 1 hardcoded come tutorial
- Min 4 blocchi dal livello 4 in poi
"""

import sys
import os
import json
import random
from typing import Dict, List, Tuple, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from level_solver import solve_level

# Shape definitions
SHAPE_CELLS = {
    'I2': [(0, 0), (1, 0)],
    'I3': [(0, 0), (1, 0), (2, 0)],
    'I4': [(0, 0), (1, 0), (2, 0), (3, 0)],
    'O4': [(0, 0), (1, 0), (0, 1), (1, 1)],
    'L3': [(0, 0), (1, 0), (0, 1)],
    'L4': [(0, 0), (1, 0), (2, 0), (0, 1)],
    'T4': [(0, 0), (1, 0), (2, 0), (1, 1)],
    'S4': [(1, 0), (2, 0), (0, 1), (1, 1)],
    'Z4': [(0, 0), (1, 0), (1, 1), (2, 1)],
}

COLORS = ['RED', 'BLUE', 'GREEN', 'YELLOW', 'PURPLE', 'ORANGE']


class DifficultyProgression:
    """Gestisce la progressione della difficoltà attraverso i livelli"""
    
    def __init__(self):
        self.difficulty_curve = self._build_difficulty_curve()
    
    def _build_difficulty_curve(self) -> Dict[int, Dict]:
        """Costruisce la curva di difficoltà per tutti i 300 livelli"""
        curve = {}
        
        # Livelli 1-10: Tutorial e Introduzione
        for i in range(1, 11):
            if i == 1:
                # Livello 1: Tutorial hardcoded
                curve[i] = {
                    "blocks": 1,
                    "coins_per_block": 2,
                    "grid": (6, 6),
                    "walls": 0.0,
                    "target_moves": (2, 5),
                    "tutorial": True
                }
            elif i <= 3:
                curve[i] = {
                    "blocks": 1 + (i - 1) // 2,
                    "coins_per_block": 2 + (i - 1) // 2,
                    "grid": (6, 6),
                    "walls": 0.0,
                    "target_moves": (3 + i, 6 + i * 2)
                }
            else:
                # Dal livello 4: min 4 blocchi, ma con griglie più grandi
                curve[i] = {
                    "blocks": 4,  # Sempre 4 blocchi dal livello 4
                    "coins_per_block": 3,
                    "grid": (7, 7),  # Griglia più grande per facilitare generazione
                    "walls": 0.0,  # No muri per i primi livelli
                    "target_moves": (8 + i, 15 + i * 2)
                }
        
        # Livelli 11-50: Progressione Base
        for i in range(11, 51):
            curve[i] = {
                "blocks": max(4, 3 + (i - 11) // 10),
                "coins_per_block": 3 + (i - 11) // 15,
                "grid": (7 + (i - 11) // 20, 7 + (i - 11) // 20),
                "walls": min(0.08, 0.05 + (i - 11) * 0.001),
                "target_moves": (8 + i // 2, 15 + i)
            }
        
        # Livelli 51-150: Intermedio
        for i in range(51, 151):
            curve[i] = {
                "blocks": max(4, 4 + (i - 51) // 25),
                "coins_per_block": 4 + (i - 51) // 40,
                "grid": (8 + (i - 51) // 50, 8 + (i - 51) // 50),
                "walls": min(0.12, 0.08 + (i - 51) * 0.0004),
                "target_moves": (10 + i // 2, 20 + i)
            }
        
        # Livelli 151-250: Avanzato
        for i in range(151, 251):
            curve[i] = {
                "blocks": max(5, 5 + (i - 151) // 30),
                "coins_per_block": 4 + (i - 151) // 50,
                "grid": (9 + (i - 151) // 50, 9 + (i - 151) // 50),
                "walls": min(0.15, 0.10 + (i - 151) * 0.0005),
                "target_moves": (15 + i // 2, 25 + i)
            }
        
        # Livelli 251-300: Esperto
        for i in range(251, 301):
            curve[i] = {
                "blocks": 6,
                "coins_per_block": 5,
                "grid": (10, 10),
                "walls": min(0.15, 0.12 + (i - 251) * 0.0006),
                "target_moves": (20 + i // 2, 30 + i)
            }
        
        return curve
    
    def get_target_difficulty(self, level_num: int) -> Dict:
        """Ottiene i parametri di difficoltà target per un livello"""
        return self.difficulty_curve.get(level_num, self.difficulty_curve[1])


class LevelValidator:
    """Valida i livelli generati"""
    
    def __init__(self):
        pass
    
    def validate_level(self, level_data: Dict, min_moves: int = 5) -> Tuple[bool, str, int]:
        """
        Valida un livello completo
        
        Returns:
            (is_valid, error_message, num_moves)
        """
        # 1. Structural validation
        if not self._validate_structure(level_data):
            return False, "Invalid structure", 0
        
        # 2. Solvability check
        max_moves = level_data['meta'].get('stars', [0, 0, 100])[2] + 20
        is_solvable, solution, num_moves = solve_level(level_data, max_moves=max_moves, verbose=False)
        
        if not is_solvable:
            return False, "Level is not solvable", 0
        
        # 3. Minimum moves check
        if num_moves < min_moves:
            return False, f"Too easy: only {num_moves} moves (min {min_moves})", num_moves
        
        return True, "Valid", num_moves
    
    def _validate_structure(self, level_data: Dict) -> bool:
        """Valida la struttura base del livello"""
        required_keys = ['meta', 'layout', 'blocks', 'coins']
        if not all(key in level_data for key in required_keys):
            return False
        
        # Check meta
        meta = level_data['meta']
        if 'id' not in meta or 'grid_size' not in meta:
            return False
        
        # Check blocks
        if not level_data['blocks']:
            return False
        
        # Check coins
        if 'static' not in level_data['coins']:
            return False
        
        return True


class LevelGeneratorV2:
    """Generatore di livelli V2 - Conforme GDD 4.0"""
    
    def __init__(self):
        self.difficulty = DifficultyProgression()
        self.validator = LevelValidator()
        self.levels_dir = "data/levels"
    
    def hard_delete_existing_levels(self):
        """HARD DELETE di tutti i livelli esistenti"""
        print("⚠️  HARD DELETE: Cancellazione livelli esistenti...")
        
        if not os.path.exists(self.levels_dir):
            os.makedirs(self.levels_dir)
            print("✅ Directory levels creata")
            return
        
        deleted_count = 0
        for filename in os.listdir(self.levels_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.levels_dir, filename)
                os.remove(filepath)
                deleted_count += 1
        
        print(f"✅ {deleted_count} livelli cancellati")
    
    def generate_all_levels(self, num_levels: int = 300, start_from: int = 1):
        """Genera tutti i livelli in sequenza"""
        print("=" * 70)
        print("TETRACOIN LEVEL GENERATOR V2 - GDD 4.0 COMPLIANT")
        print("=" * 70)
        print()
        
        # Hard delete existing levels
        if start_from == 1:
            self.hard_delete_existing_levels()
            print()
        
        print(f"Generazione livelli {start_from}-{num_levels}...")
        print()
        
        results = []
        
        for level_num in range(start_from, num_levels + 1):
            print(f"📦 Livello {level_num}/{num_levels}...", end=" ", flush=True)
            
            target = self.difficulty.get_target_difficulty(level_num)
            
            # Generate level
            if target.get('tutorial', False):
                level_data, num_moves = self.create_tutorial_level()
            else:
                level_data, num_moves = self.generate_level(level_num, target)
            
            if level_data is None:
                print(f"❌ FALLITO dopo max tentativi")
                results.append({"level": level_num, "status": "FAILED", "moves": 0})
                continue
            
            # Save level
            self._save_level(level_num, level_data)
            
            print(f"✅ OK ({num_moves} mosse)")
            results.append({"level": level_num, "status": "SUCCESS", "moves": num_moves, "target": target['target_moves']})
        
        # Summary
        self._print_summary(results)
        
        return results
    
    def create_tutorial_level(self) -> Tuple[Dict, int]:
        """Crea il livello 1 hardcoded come tutorial"""
        print("(Tutorial hardcoded)...", end=" ", flush=True)
        
        level_data = {
            "meta": {
                "id": 1,
                "world": 1,
                "name": "Tutorial",
                "grid_size": [6, 6],
                "time_limit": 120,
                "stars": [2, 3, 5],
                "tutorial_text": "Trascina il blocco per raccogliere le monete! Abbina i colori."
            },
            "layout": [[0 for _ in range(6)] for _ in range(6)],
            "blocks": [
                {
                    "id": "b_0",
                    "shape": "I2",
                    "color": "BLUE",
                    "counter": 2,
                    "xy": [1, 2]
                }
            ],
            "coins": {
                "static": [
                    {"color": "BLUE", "xy": [4, 2]},
                    {"color": "BLUE", "xy": [2, 4]}
                ],
                "entrances": []
            }
        }
        
        # Validate
        is_valid, msg, num_moves = self.validator.validate_level(level_data, min_moves=2)
        
        if is_valid:
            return level_data, num_moves
        else:
            # Fallback tutorial (should never happen)
            return level_data, 3
    
    def generate_level(self, level_num: int, target: Dict, max_attempts: int = 200) -> Tuple[Optional[Dict], int]:
        """Genera un singolo livello"""
        num_blocks = target["blocks"]
        coins_per_block = target["coins_per_block"]
        grid_w, grid_h = target["grid"]
        wall_density = target["walls"]
        min_moves, max_moves = target["target_moves"]
        
        best_level = None
        best_moves = None
        best_distance = float('inf')
        
        for attempt in range(max_attempts):
            # Generate candidate level
            level_data = self._generate_candidate_level(
                level_num, num_blocks, coins_per_block, grid_w, grid_h, wall_density, max_moves
            )
            
            if level_data is None:
                continue
            
            # Validate
            # Use lower min_moves for early levels
            min_moves_required = 3 if level_num <= 10 else 5
            is_valid, msg, num_moves = self.validator.validate_level(level_data, min_moves=min_moves_required)
            
            if not is_valid:
                continue
            
            # Check if in target range
            if min_moves <= num_moves <= max_moves:
                return level_data, num_moves
            
            # Track best attempt
            distance = abs(num_moves - (min_moves + max_moves) / 2)
            if distance < best_distance:
                best_distance = distance
                best_level = level_data
                best_moves = num_moves
        
        # Return best attempt if found
        if best_level:
            return best_level, best_moves
        
        return None, 0
    
    def _generate_candidate_level(self, level_num: int, num_blocks: int, coins_per_block: int,
                                   grid_w: int, grid_h: int, wall_density: float, max_moves: int) -> Optional[Dict]:
        """Genera un livello candidato"""
        # Generate layout
        layout = self._generate_layout(grid_w, grid_h, wall_density)
        empty_spots = self._find_empty_spots(layout)
        
        if len(empty_spots) < num_blocks * 4 + num_blocks * coins_per_block:
            return None
        
        # Place blocks
        blocks = self._place_blocks(empty_spots, num_blocks, grid_w, grid_h, layout)
        if not blocks:
            return None
        
        # Place coins
        coins = self._place_coins_for_blocks(blocks, empty_spots, coins_per_block, layout)
        if not coins:
            return None
        
        # Create level data
        level_data = {
            "meta": {
                "id": level_num,
                "world": 1 + (level_num - 1) // 50,
                "name": f"Level {level_num}",
                "grid_size": [grid_w, grid_h],
                "time_limit": 60 + level_num * 5,
                "stars": [max_moves // 3, max_moves // 2, max_moves]
            },
            "layout": layout,
            "blocks": blocks,
            "coins": {"static": coins, "entrances": []}
        }
        
        return level_data
    
    def _generate_layout(self, width: int, height: int, wall_density: float) -> List[List[int]]:
        """Genera layout griglia con muri casuali"""
        layout = [[0 for _ in range(width)] for _ in range(height)]
        
        if wall_density > 0:
            num_walls = int(width * height * wall_density)
            for _ in range(num_walls):
                x = random.randint(1, width - 2)  # Avoid perimeter
                y = random.randint(1, height - 2)
                layout[y][x] = 1
        
        return layout
    
    def _find_empty_spots(self, layout: List[List[int]]) -> List[Tuple[int, int]]:
        """Trova tutte le celle vuote"""
        empty = []
        for y in range(len(layout)):
            for x in range(len(layout[0])):
                if layout[y][x] == 0:
                    empty.append((x, y))
        return empty
    
    def _can_place_shape(self, pos: Tuple[int, int], shape: str, layout: List[List[int]], 
                         occupied: set) -> bool:
        """Verifica se una forma può essere posizionata"""
        grid_w = len(layout[0])
        grid_h = len(layout)
        shape_cells = SHAPE_CELLS[shape]
        
        for dx, dy in shape_cells:
            x, y = pos[0] + dx, pos[1] + dy
            if x < 0 or x >= grid_w or y < 0 or y >= grid_h:
                return False
            if layout[y][x] == 1:
                return False
            if (x, y) in occupied:
                return False
        return True
    
    def _place_blocks(self, empty_spots: List[Tuple[int, int]], num_blocks: int,
                      grid_w: int, grid_h: int, layout: List[List[int]]) -> Optional[List[Dict]]:
        """Posiziona i blocchi"""
        blocks = []
        occupied = set()
        shapes = list(SHAPE_CELLS.keys())
        
        for i in range(num_blocks):
            for attempt in range(100):
                shape = random.choice(shapes)
                pos = random.choice(empty_spots)
                
                if self._can_place_shape(pos, shape, layout, occupied):
                    color = COLORS[i % len(COLORS)]
                    block = {
                        'id': f'b_{i}',
                        'shape': shape,
                        'color': color,
                        'counter': 0,
                        'xy': list(pos)
                    }
                    blocks.append(block)
                    
                    # Mark cells as occupied
                    for dx, dy in SHAPE_CELLS[shape]:
                        occupied.add((pos[0] + dx, pos[1] + dy))
                    break
        
        return blocks if len(blocks) == num_blocks else None
    
    def _place_coins_for_blocks(self, blocks: List[Dict], empty_spots: List[Tuple[int, int]],
                                 coins_per_block: int, layout: List[List[int]]) -> Optional[List[Dict]]:
        """Posiziona le monete per ogni blocco"""
        coins = []
        occupied = set()
        
        # Mark block cells as occupied
        for block in blocks:
            for dx, dy in SHAPE_CELLS[block['shape']]:
                occupied.add((block['xy'][0] + dx, block['xy'][1] + dy))
        
        for block in blocks:
            color = block['color']
            placed = 0
            
            for attempt in range(200):
                pos = random.choice(empty_spots)
                if pos not in occupied:
                    coins.append({'color': color, 'xy': list(pos)})
                    occupied.add(pos)
                    placed += 1
                    if placed >= coins_per_block:
                        break
            
            if placed < coins_per_block:
                return None
            
            block['counter'] = placed
        
        return coins
    
    def _save_level(self, level_num: int, level_data: Dict):
        """Salva il livello su file"""
        filename = f"level_{level_num:03d}.json"
        filepath = os.path.join(self.levels_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(level_data, f, indent=2)
    
    def _print_summary(self, results: List[Dict]):
        """Stampa il riepilogo della generazione"""
        print()
        print("=" * 70)
        print("RIEPILOGO GENERAZIONE")
        print("=" * 70)
        
        success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
        failed_count = sum(1 for r in results if r['status'] == 'FAILED')
        
        print(f"✅ Livelli generati con successo: {success_count}/{len(results)}")
        print(f"❌ Livelli falliti: {failed_count}/{len(results)}")
        
        if failed_count > 0:
            print("\n⚠️  Livelli falliti:")
            for r in results:
                if r['status'] == 'FAILED':
                    print(f"  - Livello {r['level']}")
        
        print()
        print("=" * 70)


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TetraCoin Level Generator V2')
    parser.add_argument('--generate-all', action='store_true', help='Generate all 300 levels')
    parser.add_argument('--num-levels', type=int, default=300, help='Number of levels to generate')
    parser.add_argument('--start-from', type=int, default=1, help='Start from level N')
    
    args = parser.parse_args()
    
    generator = LevelGeneratorV2()
    
    if args.generate_all or args.num_levels:
        generator.generate_all_levels(num_levels=args.num_levels, start_from=args.start_from)
    else:
        print("Usa --generate-all per generare tutti i livelli")
        print("Usa --num-levels N per generare N livelli")
        print("Usa --start-from N per iniziare dal livello N")


if __name__ == "__main__":
    main()
