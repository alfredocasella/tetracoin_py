#!/usr/bin/env python3
"""
TetraCoin Level Generator V3 - OTTIMIZZATO
Miglioramenti:
- Generazione guidata da euristiche invece che casuale
- Pre-validazione leggera prima del solver costoso
- Algoritmo di costruzione progressiva
- Gestione intelligente dello spazio
"""

import sys
import os
import json
import random
from typing import Dict, List, Tuple, Optional, Set
from collections import deque

# Add project root to path - FIX per struttura reale
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir) if 'scripts' in script_dir else script_dir
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'scripts'))

try:
    from level_solver import solve_level
    SOLVER_AVAILABLE = True
except ImportError:
    print("⚠️  WARNING: level_solver.py non trovato - validazione completa disabilitata")
    print("    I livelli saranno generati ma non validati per solvibilità")
    SOLVER_AVAILABLE = False
    
    def solve_level(level_data, max_moves=100, verbose=False):
        """Fallback solver che assume sempre solvibile"""
        return True, [], 10

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

# Forme preferite per livelli iniziali (più semplici)
SIMPLE_SHAPES = ['I2', 'I3', 'L3', 'O4']
COMPLEX_SHAPES = ['I4', 'L4', 'T4', 'S4', 'Z4']


class SmartGridAnalyzer:
    """Analizza la griglia per capire se ha spazio sufficiente"""
    
    @staticmethod
    def calculate_connectivity(layout: List[List[int]]) -> float:
        """Calcola la connettività della griglia (% di celle raggiungibili)"""
        grid_h = len(layout)
        grid_w = len(layout[0])
        
        # Trova una cella vuota di partenza
        start = None
        for y in range(grid_h):
            for x in range(grid_w):
                if layout[y][x] == 0:
                    start = (x, y)
                    break
            if start:
                break
        
        if not start:
            return 0.0
        
        # BFS per trovare tutte le celle raggiungibili
        visited = set()
        queue = deque([start])
        visited.add(start)
        
        while queue:
            x, y = queue.popleft()
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < grid_w and 0 <= ny < grid_h and 
                    (nx, ny) not in visited and layout[ny][nx] == 0):
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        
        empty_count = sum(1 for row in layout for cell in row if cell == 0)
        return len(visited) / max(empty_count, 1)
    
    @staticmethod
    def count_open_areas(layout: List[List[int]], min_size: int = 4) -> int:
        """Conta quante aree aperte ci sono (per posizionare blocchi)"""
        grid_h = len(layout)
        grid_w = len(layout[0])
        
        count = 0
        for y in range(grid_h - 1):
            for x in range(grid_w - 1):
                # Controlla se c'è un'area 2x2 libera
                if all(layout[y+dy][x+dx] == 0 
                       for dy in range(2) for dx in range(2)):
                    count += 1
        
        return count


class DifficultyProgression:
    """Gestisce la progressione della difficoltà attraverso i livelli"""
    
    def __init__(self):
        self.difficulty_curve = self._build_difficulty_curve()
    
    def _build_difficulty_curve(self) -> Dict[int, Dict]:
        """Curva di difficoltà OTTIMIZZATA con griglie più grandi"""
        curve = {}
        
        # Livelli 1-10: Tutorial - GRIGLIE PIÙ GRANDI
        for i in range(1, 11):
            if i == 1:
                curve[i] = {
                    "blocks": 1,
                    "coins_per_block": 2,
                    "grid": (6, 6),
                    "walls": 0.0,
                    "target_moves": (2, 5),
                    "tutorial": True,
                    "shapes": SIMPLE_SHAPES
                }
            elif i <= 3:
                curve[i] = {
                    "blocks": 1 + (i - 1) // 2,
                    "coins_per_block": 2 + (i - 1) // 2,
                    "grid": (7, 7),  # Aumentata da 6x6
                    "walls": 0.0,
                    "target_moves": (3 + i, 6 + i * 2),
                    "shapes": SIMPLE_SHAPES
                }
            else:
                # Dal livello 4: GRIGLIA MOLTO PIÙ GRANDE per 4 blocchi
                curve[i] = {
                    "blocks": min(3, 2 + (i - 4) // 3),  # Crescita graduale
                    "coins_per_block": 3,
                    "grid": (9, 9),  # Aumentata da 7x7 a 9x9
                    "walls": 0.0,
                    "target_moves": (8 + i, 15 + i * 2),
                    "shapes": SIMPLE_SHAPES if i <= 6 else SIMPLE_SHAPES + COMPLEX_SHAPES[:2]
                }
        
        # Livelli 11-50: Progressione Base - SPAZIO ADEGUATO
        for i in range(11, 51):
            num_blocks = min(5, 3 + (i - 11) // 10)
            curve[i] = {
                "blocks": num_blocks,
                "coins_per_block": 3 + (i - 11) // 15,
                "grid": (8 + num_blocks // 2, 8 + num_blocks // 2),  # Scala con num blocchi
                "walls": min(0.06, 0.02 + (i - 11) * 0.001),  # Meno muri
                "target_moves": (8 + i // 2, 15 + i),
                "shapes": SIMPLE_SHAPES + COMPLEX_SHAPES[:3]
            }
        
        # Livelli 51-150: Intermedio
        for i in range(51, 151):
            num_blocks = min(6, 4 + (i - 51) // 25)
            curve[i] = {
                "blocks": num_blocks,
                "coins_per_block": 4 + (i - 51) // 40,
                "grid": (9 + num_blocks // 2, 9 + num_blocks // 2),
                "walls": min(0.10, 0.05 + (i - 51) * 0.0004),
                "target_moves": (10 + i // 2, 20 + i),
                "shapes": SIMPLE_SHAPES + COMPLEX_SHAPES
            }
        
        # Livelli 151-250: Avanzato
        for i in range(151, 251):
            num_blocks = min(7, 5 + (i - 151) // 30)
            curve[i] = {
                "blocks": num_blocks,
                "coins_per_block": 4 + (i - 151) // 50,
                "grid": (10 + num_blocks // 3, 10 + num_blocks // 3),
                "walls": min(0.12, 0.08 + (i - 151) * 0.0004),
                "target_moves": (15 + i // 2, 25 + i),
                "shapes": SIMPLE_SHAPES + COMPLEX_SHAPES
            }
        
        # Livelli 251-300: Esperto
        for i in range(251, 301):
            curve[i] = {
                "blocks": 6,
                "coins_per_block": 5,
                "grid": (12, 12),  # Molto più grande per livelli finali
                "walls": min(0.12, 0.08 + (i - 251) * 0.0004),
                "target_moves": (20 + i // 2, 30 + i),
                "shapes": SIMPLE_SHAPES + COMPLEX_SHAPES
            }
        
        return curve
    
    def get_target_difficulty(self, level_num: int) -> Dict:
        """Ottiene i parametri di difficoltà target per un livello"""
        return self.difficulty_curve.get(level_num, self.difficulty_curve[1])


class LevelValidator:
    """Valida i livelli generati con pre-validazione rapida"""
    
    def __init__(self):
        self.analyzer = SmartGridAnalyzer()
    
    def quick_validate(self, level_data: Dict) -> Tuple[bool, str]:
        """Pre-validazione veloce senza solver (euristiche)"""
        
        # 1. Verifica connettività
        connectivity = self.analyzer.calculate_connectivity(level_data['layout'])
        if connectivity < 0.7:  # Almeno 70% di celle raggiungibili
            return False, f"Low connectivity: {connectivity:.2f}"
        
        # 2. Verifica spazio per blocchi
        open_areas = self.analyzer.count_open_areas(level_data['layout'])
        num_blocks = len(level_data['blocks'])
        if open_areas < num_blocks * 2:
            return False, f"Insufficient space: {open_areas} areas for {num_blocks} blocks"
        
        # 3. Verifica che ci siano abbastanza monete
        total_coins_needed = sum(b['counter'] for b in level_data['blocks'])
        total_coins = len(level_data['coins']['static'])
        if total_coins < total_coins_needed:
            return False, f"Not enough coins: {total_coins}/{total_coins_needed}"
        
        return True, "Quick validation passed"
    
    def validate_level(self, level_data: Dict, min_moves: int = 5) -> Tuple[bool, str, int]:
        """Validazione completa con solver"""
        
        # Prima: validazione rapida
        quick_ok, quick_msg = self.quick_validate(level_data)
        if not quick_ok:
            return False, f"Quick check failed: {quick_msg}", 0
        
        # Poi: validazione strutturale
        if not self._validate_structure(level_data):
            return False, "Invalid structure", 0
        
        # Infine: solver (costoso)
        max_moves = level_data['meta'].get('stars', [0, 0, 100])[2] + 20
        is_solvable, solution, num_moves = solve_level(level_data, max_moves=max_moves, verbose=False)
        
        if not is_solvable:
            return False, "Level is not solvable", 0
        
        if num_moves < min_moves:
            return False, f"Too easy: only {num_moves} moves", num_moves
        
        return True, "Valid", num_moves
    
    def _validate_structure(self, level_data: Dict) -> bool:
        """Valida la struttura base del livello"""
        required_keys = ['meta', 'layout', 'blocks', 'coins']
        if not all(key in level_data for key in required_keys):
            return False
        
        meta = level_data['meta']
        if 'id' not in meta or 'grid_size' not in meta:
            return False
        
        if not level_data['blocks']:
            return False
        
        if 'static' not in level_data['coins']:
            return False
        
        return True


class SmartLevelGenerator:
    """Generatore V3 con costruzione guidata"""
    
    def __init__(self):
        self.difficulty = DifficultyProgression()
        self.validator = LevelValidator()
        self.analyzer = SmartGridAnalyzer()
        self.levels_dir = "data/levels"
    
    def generate_level(self, level_num: int, target: Dict, max_attempts: int = 100) -> Tuple[Optional[Dict], int]:
        """Genera un livello con approccio smart"""
        
        num_blocks = target["blocks"]
        coins_per_block = target["coins_per_block"]
        grid_w, grid_h = target["grid"]
        wall_density = target["walls"]
        min_moves, max_moves = target["target_moves"]
        allowed_shapes = target.get("shapes", list(SHAPE_CELLS.keys()))
        
        best_level = None
        best_moves = None
        best_distance = float('inf')
        
        attempts_with_quick_pass = 0
        
        for attempt in range(max_attempts):
            # FASE 1: Genera layout intelligente
            layout = self._generate_smart_layout(grid_w, grid_h, wall_density, num_blocks)
            
            # Pre-check: connettività minima
            connectivity = self.analyzer.calculate_connectivity(layout)
            if connectivity < 0.7:
                continue
            
            empty_spots = self._find_empty_spots(layout)
            
            # FASE 2: Posizionamento guidato dei blocchi
            blocks = self._place_blocks_smart(
                empty_spots, num_blocks, grid_w, grid_h, layout, allowed_shapes
            )
            
            if not blocks:
                continue
            
            # FASE 3: Posizionamento strategico monete
            coins = self._place_coins_strategic(
                blocks, empty_spots, coins_per_block, layout
            )
            
            if not coins:
                continue
            
            # Crea level data
            level_data = self._create_level_data(
                level_num, layout, blocks, coins, max_moves
            )
            
            # QUICK VALIDATION (veloce)
            quick_ok, quick_msg = self.validator.quick_validate(level_data)
            if not quick_ok:
                continue
            
            attempts_with_quick_pass += 1
            
            # FULL VALIDATION (costoso - solo se quick pass)
            min_moves_required = 3 if level_num <= 10 else 5
            is_valid, msg, num_moves = self.validator.validate_level(
                level_data, min_moves=min_moves_required
            )
            
            if not is_valid:
                continue
            
            # Cerca livello nel range target
            if min_moves <= num_moves <= max_moves:
                return level_data, num_moves
            
            # Traccia il migliore
            distance = abs(num_moves - (min_moves + max_moves) / 2)
            if distance < best_distance:
                best_distance = distance
                best_level = level_data
                best_moves = num_moves
        
        # Statistiche debug
        if best_level and attempts_with_quick_pass > 0:
            pass  # Success path
        
        return best_level, best_moves if best_level else 0
    
    def _generate_smart_layout(self, width: int, height: int, wall_density: float, 
                               num_blocks: int) -> List[List[int]]:
        """Genera layout che favorisce la connettività"""
        layout = [[0 for _ in range(width)] for _ in range(height)]
        
        if wall_density <= 0:
            return layout
        
        # Strategia: metti muri ai bordi/angoli, non al centro
        num_walls = int(width * height * wall_density)
        placed = 0
        
        # Preferisci posizioni periferiche
        border_positions = []
        center_positions = []
        
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                dist_to_edge = min(x, y, width - 1 - x, height - 1 - y)
                if dist_to_edge <= 1:
                    border_positions.append((x, y))
                else:
                    center_positions.append((x, y))
        
        # 70% muri ai bordi, 30% al centro
        border_walls = int(num_walls * 0.7)
        center_walls = num_walls - border_walls
        
        random.shuffle(border_positions)
        random.shuffle(center_positions)
        
        for x, y in border_positions[:border_walls]:
            layout[y][x] = 1
            placed += 1
        
        for x, y in center_positions[:center_walls]:
            layout[y][x] = 1
            placed += 1
        
        return layout
    
    def _find_empty_spots(self, layout: List[List[int]]) -> List[Tuple[int, int]]:
        """Trova celle vuote"""
        empty = []
        for y in range(len(layout)):
            for x in range(len(layout[0])):
                if layout[y][x] == 0:
                    empty.append((x, y))
        return empty
    
    def _place_blocks_smart(self, empty_spots: List[Tuple[int, int]], num_blocks: int,
                           grid_w: int, grid_h: int, layout: List[List[int]],
                           allowed_shapes: List[str]) -> Optional[List[Dict]]:
        """Posizionamento intelligente: distribuiti spazialmente"""
        
        blocks = []
        occupied = set()
        
        # Dividi la griglia in zone
        zones = self._divide_into_zones(grid_w, grid_h, num_blocks)
        
        for i, zone in enumerate(zones[:num_blocks]):
            # Trova spot in questa zona
            zone_spots = [pos for pos in empty_spots if self._is_in_zone(pos, zone)]
            
            if not zone_spots:
                zone_spots = empty_spots  # Fallback
            
            # Prova forme dall'elenco consentito
            random.shuffle(allowed_shapes)
            
            placed = False
            for shape in allowed_shapes:
                random.shuffle(zone_spots)
                for pos in zone_spots:
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
                        
                        # Segna occupato
                        for dx, dy in SHAPE_CELLS[shape]:
                            occupied.add((pos[0] + dx, pos[1] + dy))
                        
                        placed = True
                        break
                
                if placed:
                    break
            
            if not placed:
                return None
        
        return blocks if len(blocks) == num_blocks else None
    
    def _divide_into_zones(self, grid_w: int, grid_h: int, num_zones: int) -> List[Tuple]:
        """Divide la griglia in zone per distribuire blocchi"""
        zones = []
        
        if num_zones <= 2:
            # Metà sinistra, metà destra
            zones.append((0, 0, grid_w // 2, grid_h))
            zones.append((grid_w // 2, 0, grid_w, grid_h))
        elif num_zones <= 4:
            # Quadranti
            zones.append((0, 0, grid_w // 2, grid_h // 2))
            zones.append((grid_w // 2, 0, grid_w, grid_h // 2))
            zones.append((0, grid_h // 2, grid_w // 2, grid_h))
            zones.append((grid_w // 2, grid_h // 2, grid_w, grid_h))
        else:
            # Griglia 3x3 o simile
            rows = min(3, (num_zones + 2) // 3)
            cols = (num_zones + rows - 1) // rows
            
            cell_w = grid_w // cols
            cell_h = grid_h // rows
            
            for r in range(rows):
                for c in range(cols):
                    zones.append((
                        c * cell_w,
                        r * cell_h,
                        min((c + 1) * cell_w, grid_w),
                        min((r + 1) * cell_h, grid_h)
                    ))
        
        return zones
    
    def _is_in_zone(self, pos: Tuple[int, int], zone: Tuple[int, int, int, int]) -> bool:
        """Verifica se una posizione è in una zona"""
        x, y = pos
        x1, y1, x2, y2 = zone
        return x1 <= x < x2 and y1 <= y < y2
    
    def _can_place_shape(self, pos: Tuple[int, int], shape: str, 
                        layout: List[List[int]], occupied: set) -> bool:
        """Verifica se forma può essere piazzata"""
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
    
    def _place_coins_strategic(self, blocks: List[Dict], empty_spots: List[Tuple[int, int]],
                               coins_per_block: int, layout: List[List[int]]) -> Optional[List[Dict]]:
        """Posiziona monete con strategia: lontano dal blocco"""
        coins = []
        occupied = set()
        
        # Segna blocchi come occupati
        for block in blocks:
            for dx, dy in SHAPE_CELLS[block['shape']]:
                occupied.add((block['xy'][0] + dx, block['xy'][1] + dy))
        
        for block in blocks:
            color = block['color']
            block_pos = tuple(block['xy'])
            placed = 0
            
            # Ordina spot per distanza dal blocco (preferisci lontani)
            sorted_spots = sorted(
                [pos for pos in empty_spots if pos not in occupied],
                key=lambda p: abs(p[0] - block_pos[0]) + abs(p[1] - block_pos[1]),
                reverse=True  # Lontani prima
            )
            
            for pos in sorted_spots:
                if placed >= coins_per_block:
                    break
                
                coins.append({'color': color, 'xy': list(pos)})
                occupied.add(pos)
                placed += 1
            
            if placed < coins_per_block:
                return None
            
            block['counter'] = placed
        
        return coins
    
    def _create_level_data(self, level_num: int, layout: List[List[int]], 
                          blocks: List[Dict], coins: List[Dict], max_moves: int) -> Dict:
        """Crea struttura dati livello"""
        grid_h = len(layout)
        grid_w = len(layout[0])
        
        return {
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
    
    def hard_delete_existing_levels(self):
        """Cancella livelli esistenti"""
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
    
    def create_tutorial_level(self) -> Tuple[Dict, int]:
        """Crea livello 1 tutorial"""
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
        
        is_valid, msg, num_moves = self.validator.validate_level(level_data, min_moves=2)
        return level_data, num_moves if is_valid else 3
    
    def generate_all_levels(self, num_levels: int = 300, start_from: int = 1):
        """Genera tutti i livelli"""
        print("=" * 70)
        print("TETRACOIN LEVEL GENERATOR V3 - OTTIMIZZATO")
        print("=" * 70)
        print()
        
        if start_from == 1:
            self.hard_delete_existing_levels()
            print()
        
        print(f"Generazione livelli {start_from}-{num_levels}...")
        print()
        
        results = []
        
        for level_num in range(start_from, num_levels + 1):
            print(f"📦 Livello {level_num}/{num_levels}...", end=" ", flush=True)
            
            target = self.difficulty.get_target_difficulty(level_num)
            
            if target.get('tutorial', False):
                level_data, num_moves = self.create_tutorial_level()
            else:
                level_data, num_moves = self.generate_level(level_num, target)
            
            if level_data is None:
                print(f"❌ FALLITO dopo max tentativi")
                results.append({"level": level_num, "status": "FAILED", "moves": 0})
                continue
            
            self._save_level(level_num, level_data)
            
            print(f"✅ OK ({num_moves} mosse)")
            results.append({
                "level": level_num, 
                "status": "SUCCESS", 
                "moves": num_moves,
                "target": target['target_moves']
            })
        
        self._print_summary(results)
        return results
    
    def generate_random_test_levels(self, count: int):
        """Genera livelli casuali per test (non sostituisce i livelli ufficiali)"""
        print("=" * 70)
        print(f"GENERAZIONE {count} LIVELLI CASUALI PER TEST")
        print("=" * 70)
        print()
        
        # Crea directory test se non esiste
        test_dir = os.path.join(self.levels_dir, "test")
        os.makedirs(test_dir, exist_ok=True)
        
        results = []
        
        for i in range(1, count + 1):
            print(f"🧪 Test Level {i}/{count}...", end=" ", flush=True)
            
            # Difficoltà casuale tra 1 e 300
            random_difficulty_level = random.randint(1, 300)
            target = self.difficulty.get_target_difficulty(random_difficulty_level)
            
            level_data, num_moves = self.generate_level(i, target, max_attempts=100)
            
            if level_data is None:
                print(f"❌ FALLITO")
                results.append({"test": i, "status": "FAILED"})
                continue
            
            # Salva come test_XXX.json
            filename = f"test_{i:03d}.json"
            filepath = os.path.join(test_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(level_data, f, indent=2)
            
            print(f"✅ OK (Difficoltà ~{random_difficulty_level}, {num_moves} mosse)")
            print(f"   📁 Salvato: {filepath}")
            
            results.append({
                "test": i,
                "status": "SUCCESS",
                "difficulty_ref": random_difficulty_level,
                "moves": num_moves
            })
        
        print()
        print("=" * 70)
        print("RIEPILOGO TEST")
        print("=" * 70)
        success = sum(1 for r in results if r['status'] == 'SUCCESS')
        print(f"✅ Generati: {success}/{count}")
        print(f"📁 Directory: {test_dir}")
        print()
    
    def generate_test_at_difficulty(self, difficulty_level: int, count: int = 5):
        """Genera livelli di test con una difficoltà specifica"""
        print("=" * 70)
        print(f"GENERAZIONE TEST LIVELLI - DIFFICOLTÀ LIVELLO {difficulty_level}")
        print("=" * 70)
        print()
        
        # Crea directory test se non esiste
        test_dir = os.path.join(self.levels_dir, "test")
        os.makedirs(test_dir, exist_ok=True)
        
        target = self.difficulty.get_target_difficulty(difficulty_level)
        
        print(f"Parametri difficoltà:")
        print(f"  • Blocchi: {target['blocks']}")
        print(f"  • Monete per blocco: {target['coins_per_block']}")
        print(f"  • Griglia: {target['grid'][0]}x{target['grid'][1]}")
        print(f"  • Densità muri: {target['walls']:.2%}")
        print(f"  • Target mosse: {target['target_moves'][0]}-{target['target_moves'][1]}")
        print()
        
        results = []
        
        for i in range(1, count + 1):
            print(f"🧪 Test {i}/{count}...", end=" ", flush=True)
            
            level_data, num_moves = self.generate_level(difficulty_level * 1000 + i, target, max_attempts=150)
            
            if level_data is None:
                print(f"❌ FALLITO")
                results.append({"test": i, "status": "FAILED"})
                continue
            
            # Salva con nome descrittivo
            filename = f"test_diff{difficulty_level:03d}_{i:02d}.json"
            filepath = os.path.join(test_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(level_data, f, indent=2)
            
            print(f"✅ OK ({num_moves} mosse)")
            print(f"   📁 {filepath}")
            
            results.append({
                "test": i,
                "status": "SUCCESS",
                "moves": num_moves
            })
        
        print()
        print("=" * 70)
        print("RIEPILOGO TEST")
        print("=" * 70)
        success = sum(1 for r in results if r['status'] == 'SUCCESS')
        print(f"✅ Generati: {success}/{count}")
        if success > 0:
            avg_moves = sum(r['moves'] for r in results if r['status'] == 'SUCCESS') / success
            print(f"📊 Media mosse: {avg_moves:.1f}")
        print(f"📁 Directory: {test_dir}")
        print()
    
    def _save_level(self, level_num: int, level_data: Dict):
        """Salva livello su file"""
        filename = f"level_{level_num:03d}.json"
        filepath = os.path.join(self.levels_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(level_data, f, indent=2)
    
    def _print_summary(self, results: List[Dict]):
        """Stampa riepilogo"""
        print()
        print("=" * 70)
        print("RIEPILOGO GENERAZIONE")
        print("=" * 70)
        
        success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
        failed_count = sum(1 for r in results if r['status'] == 'FAILED')
        
        print(f"✅ Livelli generati: {success_count}/{len(results)}")
        print(f"❌ Livelli falliti: {failed_count}/{len(results)}")
        
        if failed_count > 0:
            print("\n⚠️  Livelli falliti:")
            for r in results:
                if r['status'] == 'FAILED':
                    print(f"  - Livello {r['level']}")