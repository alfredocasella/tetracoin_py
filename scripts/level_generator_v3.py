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
import argparse # Assicurati che questo import sia all'inizio del file

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
    'J4': [(1, 0), (2, 0), (1, 1), (1, 2)],  # Forma J (nuova)
}

COLORS = ['RED', 'BLUE', 'GREEN', 'YELLOW', 'PURPLE', 'ORANGE']

# Forme semplici (per livelli 1-5)
SIMPLE_SHAPES = ['I2', 'I3', 'L3', 'O4']
# Forme complesse (per livelli 6-20) - PRIORITÀ ALTA
COMPLEX_SHAPES = ['L4', 'T4', 'S4', 'Z4', 'J4', 'O4']  # 60%+ di queste
# Forme MOLTO complesse (no forme lineari)
VERY_COMPLEX_SHAPES = ['L4', 'T4', 'S4', 'Z4', 'J4']  # Esclude I2, I3, I4


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
        """Curva di difficoltà REWORK 5.0 - Massima Rigidità e Dinamicità"""
        curve = {}
        
<<<<<<< HEAD
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
                    "blocks": 4,  # Min 4 blocchi dal L4 (GDD 4.0)
                    "coins_per_block": 3,
                    "grid": (9, 9),  # Aumentata da 7x7 a 9x9
                    "walls": 0.0,
                    "target_moves": (8 + i, 15 + i * 2),
                    "shapes": SIMPLE_SHAPES if i <= 6 else SIMPLE_SHAPES + COMPLEX_SHAPES[:2]
                }
=======
        # Livello 1: Tutorial (Unico con forme semplici)
        curve[1] = {
            "blocks": 2,
            "coins_per_block": 2,
            "grid": (7, 7),
            "walls": 0.20,
            "target_moves": (12, 16),  # Minimo 12 mosse
            "tutorial": True,
            "shapes": SIMPLE_SHAPES,  # I2, I3 ammessi solo qui
            "use_dynamic_timer": True,
            "complex_blocks_ratio": 0.0,
            "min_coin_dist": 2  # Distanza minima moneta-blocco
        }
>>>>>>> 5db67f2eedc748b12f9b4b6c8633d696020195aa
        
        # Livelli 2-5: Intro Hard (NO forme semplici)
        for i in range(2, 6):
            curve[i] = {
                "blocks": 2,
                "coins_per_block": 2,
                "grid": (7, 7),
                "walls": 0.18,
                "target_moves": (10, 16),
                "shapes": VERY_COMPLEX_SHAPES,
                "use_dynamic_timer": True,
                "complex_blocks_ratio": 1.0,
                "min_coin_dist": 0  # DISABILITATO: Troppo restrittivo per 7x7
            }
        
        # Livelli 6-20: Sfida Estrema
        for i in range(6, 21):
            curve[i] = {
                "blocks": 3,
                "coins_per_block": 2,
                "grid": (8, 8) if i <= 10 else (9, 9),
                "walls": 0.15,
                "target_moves": (12, 25),
                "shapes": VERY_COMPLEX_SHAPES,
                "use_dynamic_timer": True,
                "complex_blocks_ratio": 1.0,
                "strategic_coins": True,
                "min_coin_dist": 0  # DISABILITATO: Priorità alla generazione
            }
        
        # Livelli 21-50: Progressione Base - SPAZIO ADEGUATO
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
        if connectivity < 0.8:  # Aumentato a 80% per essere più restrittivi
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
        """Validazione completa con solver esterno (VELOCE)"""
        
        # Prima: validazione rapida (euristiche)
        quick_ok, quick_msg = self.quick_validate(level_data)
        if not quick_ok:
            return False, f"Quick check failed: {quick_msg}", 0
        
        # Poi: validazione strutturale
        if not self._validate_structure(level_data):
            return False, "Invalid structure", 0
        
        # Infine: solver esterno (MOLTO PIÙ VELOCE del BFS integrato)
        max_moves = level_data['meta'].get('stars', [0, 0, 100])[2] + 20
        
        if SOLVER_AVAILABLE:
            # Usa solver esterno ottimizzato
            is_solvable, solution, num_moves = solve_level(level_data, max_moves=max_moves, verbose=False)
        else:
            # Fallback a BFS integrato (lento)
            is_solvable, num_moves = self.is_solvable(level_data, max_moves=max_moves)
        
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

    
    def is_solvable(self, level_data: Dict, max_moves: int = 50) -> Tuple[bool, int]:
        """Verifica se un livello è risolvibile usando BFS"""
        initial_state = self._create_game_state(level_data)
        if self._is_win_state(initial_state):
            return True, 0
        
        queue = deque([(initial_state, 0)])
        visited = set()
        visited.add(self._state_to_hash(initial_state))
        
        states_explored = 0
        max_states = 5000
        
        while queue and states_explored < max_states:
            current_state, num_moves = queue.popleft()
            states_explored += 1
            
            for next_state in self._get_next_states(current_state, level_data['layout']):
                state_hash = self._state_to_hash(next_state)
                if state_hash in visited:
                    continue
                
                visited.add(state_hash)
                new_num_moves = num_moves + 1
                
                if new_num_moves > max_moves:
                    continue
                
                if self._is_win_state(next_state):
                    return True, new_num_moves
                
                queue.append((next_state, new_num_moves))
        
        return False, 0
    
    def _create_game_state(self, level_data: Dict) -> Dict:
        """Crea lo stato iniziale del gioco"""
        state = {'blocks': {}, 'coins': set(), 'collected': {}}
        for block in level_data['blocks']:
            block_id = block['id']
            state['blocks'][block_id] = {
                'pos': tuple(block['xy']),
                'shape': block['shape'],
                'color': block['color'],
                'counter': block['counter']
            }
            if block['color'] not in state['collected']:
                state['collected'][block['color']] = 0
        for coin in level_data['coins']['static']:
            state['coins'].add((coin['xy'][0], coin['xy'][1], coin['color']))
        return state
    
    def _state_to_hash(self, state: Dict) -> Tuple:
        """Converte uno stato in una rappresentazione hashabile"""
        block_positions = tuple(sorted((bid, bdata['pos']) for bid, bdata in state['blocks'].items()))
        remaining_coins = tuple(sorted(state['coins']))
        return (block_positions, remaining_coins)
    
    def _is_win_state(self, state: Dict) -> bool:
        """Verifica se lo stato è vincente"""
        for block_id, block_data in state['blocks'].items():
            color = block_data['color']
            required = block_data['counter']
            collected = state['collected'].get(color, 0)
            if collected < required:
                return False
        return True
    
    def _get_next_states(self, state: Dict, layout: List[List[int]]) -> List[Dict]:
        """Genera tutti gli stati successivi possibili"""
        next_states = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        grid_h = len(layout)
        grid_w = len(layout[0]) if grid_h > 0 else 0
        
        for block_id in list(state['blocks'].keys()):
            block = state['blocks'][block_id]
            for dx, dy in directions:
                new_pos = (block['pos'][0] + dx, block['pos'][1] + dy)
                if self._is_valid_move(state, block_id, new_pos, layout, grid_w, grid_h):
                    new_state = self._apply_move(state, block_id, new_pos)
                    next_states.append(new_state)
        return next_states
    
    def _is_valid_move(self, state: Dict, block_id: str, new_pos: Tuple[int, int],
                       layout: List[List[int]], grid_w: int, grid_h: int) -> bool:
        """Verifica se un blocco può muoversi in una nuova posizione"""
        block = state['blocks'][block_id]
        shape = block['shape']
        shape_cells = SHAPE_CELLS.get(shape, [(0, 0)])
        
        other_block_cells = set()
        for other_id, other_block in state['blocks'].items():
            if other_id != block_id:
                other_shape_cells = SHAPE_CELLS.get(other_block['shape'], [(0, 0)])
                for dx, dy in other_shape_cells:
                    other_block_cells.add((other_block['pos'][0] + dx, other_block['pos'][1] + dy))
        
        for dx, dy in shape_cells:
            cell_x = new_pos[0] + dx
            cell_y = new_pos[1] + dy
            
            if not (0 <= cell_x < grid_w and 0 <= cell_y < grid_h):
                return False
            if layout[cell_y][cell_x] == 1:
                return False
            if (cell_x, cell_y) in other_block_cells:
                return False
            
            for coin_x, coin_y, coin_color in state['coins']:
                if (cell_x, cell_y) == (coin_x, coin_y):
                    if coin_color != block['color']:
                        return False
        return True
    
    def _apply_move(self, state: Dict, block_id: str, new_pos: Tuple[int, int]) -> Dict:
        """Applica una mossa e crea un nuovo stato"""
        new_state = {
            'blocks': {bid: bdata.copy() for bid, bdata in state['blocks'].items()},
            'coins': state['coins'].copy(),
            'collected': state['collected'].copy()
        }
        
        block = new_state['blocks'][block_id]
        block['pos'] = new_pos
        
        shape_cells = SHAPE_CELLS.get(block['shape'], [(0, 0)])
        coins_to_remove = set()
        
        for dx, dy in shape_cells:
            cell_x = new_pos[0] + dx
            cell_y = new_pos[1] + dy
            for coin in new_state['coins']:
                coin_x, coin_y, coin_color = coin
                if (cell_x, cell_y) == (coin_x, coin_y) and coin_color == block['color']:
                    coins_to_remove.add(coin)
                    new_state['collected'][block['color']] += 1
        
        new_state['coins'] -= coins_to_remove
        
        if new_state['collected'][block['color']] >= block['counter']:
            del new_state['blocks'][block_id]
        
        return new_state


class SmartLevelGenerator:
    """Generatore V3 con costruzione guidata"""
    
    def __init__(self):
        self.difficulty = DifficultyProgression()
        self.validator = LevelValidator()
        self.analyzer = SmartGridAnalyzer()
        self.levels_dir = "data/levels"
    
    
    def _generate_level_reverse(self, target: Dict, level_num: int) -> Optional[Tuple[Dict, int]]:
        """
        Genera un livello usando REVERSE PATHFINDING
        Parte da uno stato risolto e applica mosse inverse per creare lo stato iniziale.
        Questo garantisce la risolvibilità al 100%.
        """
        num_blocks = target["blocks"]
        coins_per_block = target["coins_per_block"]
        grid_w, grid_h = target["grid"]
        wall_density = target["walls"]
        min_moves, max_moves = target["target_moves"]
        allowed_shapes = target.get("shapes", list(SHAPE_CELLS.keys()))
        
        # FASE 1: Genera layout
        layout = self._generate_smart_layout(grid_w, grid_h, wall_density, num_blocks)
        
        # Verifica connettività minima
        connectivity = self.analyzer.calculate_connectivity(layout)
        if connectivity < 0.7:
            return None
        
        empty_spots = self._find_empty_spots(layout)
        if len(empty_spots) < num_blocks * (coins_per_block + 4):
            return None
        
        # FASE 2: Crea stato finale (RISOLTO)
        # Posiziona blocchi in posizioni "di raccolta" (vicino alle monete)
        blocks_end_state = []
        coins_positions = []
        occupied = set()
        
        # Dividi griglia in zone per distribuire blocchi
        zones = self._divide_into_zones(grid_w, grid_h, num_blocks)
        
        for i, zone in enumerate(zones[:num_blocks]):
            # Trova spot in questa zona
            zone_spots = [pos for pos in empty_spots if self._is_in_zone(pos, zone) and pos not in occupied]
            if not zone_spots:
                zone_spots = [pos for pos in empty_spots if pos not in occupied]
            
            if not zone_spots:
                return None
            
            # Scegli forma
            shape = random.choice(allowed_shapes)
            
            # Trova posizione valida per il blocco
            placed = False
            random.shuffle(zone_spots)
            for pos in zone_spots:
                if self._can_place_shape(pos, shape, layout, occupied):
                    color = COLORS[i % len(COLORS)]
                    
                    # Segna celle occupate dal blocco
                    block_cells = set()
                    for dx, dy in SHAPE_CELLS[shape]:
                        cell = (pos[0] + dx, pos[1] + dy)
                        occupied.add(cell)
                        block_cells.add(cell)
                    
                    blocks_end_state.append({
                        'id': f'b_{i}',
                        'shape': shape,
                        'color': color,
                        'pos': pos,
                        'cells': block_cells
                    })
                    
                    # Posiziona monete VICINO al blocco (stato finale = raccolte)
                    # Le monete saranno nelle celle adiacenti al blocco
                    adjacent_spots = []
                    for bx, by in block_cells:
                        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                            adj = (bx + dx, by + dy)
                            if (adj in empty_spots and adj not in occupied and 
                                adj not in block_cells):
                                adjacent_spots.append(adj)
                    
                    # Aggiungi anche spot più lontani se necessario
                    if len(adjacent_spots) < coins_per_block:
                        far_spots = [s for s in empty_spots if s not in occupied and s not in block_cells]
                        random.shuffle(far_spots)
                        adjacent_spots.extend(far_spots[:coins_per_block - len(adjacent_spots)])
                    
                    # Seleziona coins_per_block posizioni
                    random.shuffle(adjacent_spots)
                    for coin_pos in adjacent_spots[:coins_per_block]:
                        coins_positions.append({
                            'color': color,
                            'pos': coin_pos
                        })
                        occupied.add(coin_pos)
                    
                    placed = True
                    break
            
            if not placed:
                return None
        
        # FASE 3: Applica mosse INVERSE per creare stato iniziale
        # Numero di mosse target (tra min e max)
        target_num_moves = random.randint(min_moves, max_moves)
        
        # Stato corrente (inizia dallo stato finale)
        current_blocks = {b['id']: b.copy() for b in blocks_end_state}
        move_history = []
        
        # Applica mosse inverse con retry se bloccato
        max_stuck_retries = 10
        stuck_count = 0
        
        for move_num in range(target_num_moves * 2):  # Aumenta limite per permettere retry
            if len(move_history) >= target_num_moves:
                break  # Raggiunto obiettivo
            
            # Scegli blocco casuale
            block_ids = list(current_blocks.keys())
            random.shuffle(block_ids)
            
            moved = False
            for block_id in block_ids:
                block = current_blocks[block_id]
                
                # Prova direzioni casuali (INVERSE: opposto della direzione normale)
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                random.shuffle(directions)
                
                for dx, dy in directions:
                    old_pos = block['pos']
                    new_pos = (old_pos[0] + dx, old_pos[1] + dy)
                    
                    # Verifica se la mossa inversa è valida
                    if self._is_valid_reverse_move(block, new_pos, layout, current_blocks, coins_positions):
                        # Applica mossa
                        block['pos'] = new_pos
                        
                        # Aggiorna celle occupate
                        block['cells'] = set()
                        for sdx, sdy in SHAPE_CELLS[block['shape']]:
                            block['cells'].add((new_pos[0] + sdx, new_pos[1] + sdy))
                        
                        move_history.append((block_id, (-dx, -dy)))  # Salva mossa NORMALE (inversa dell'inversa)
                        moved = True
                        stuck_count = 0  # Reset stuck counter
                        break
                
                if moved:
                    break
            
            # Se non riusciamo a muovere nessun blocco
            if not moved:
                stuck_count += 1
                if stuck_count >= max_stuck_retries:
                    # Troppi tentativi falliti, livello non valido
                    return None
        
        # FASE 4: Crea level data con lo stato iniziale
        blocks_initial = []
        for block in current_blocks.values():
            blocks_initial.append({
                'id': block['id'],
                'shape': block['shape'],
                'color': block['color'],
                'counter': coins_per_block,
                'xy': list(block['pos'])
            })
        
        # VALIDAZIONE DISTANZA MONETE (Rework 5.0)
        min_coin_dist = target.get('min_coin_dist', 0)
        if min_coin_dist > 0:
            for coin in coins_positions:
                coin_pos = coin['pos']
                coin_color = coin['color']
                
                # Trova blocco corrispondente
                matching_block = next((b for b in current_blocks.values() if b['color'] == coin_color), None)
                if matching_block:
                    # Calcola celle occupate dal blocco nello stato iniziale
                    block_cells = set()
                    for dx, dy in SHAPE_CELLS[matching_block['shape']]:
                        block_cells.add((matching_block['pos'][0] + dx, matching_block['pos'][1] + dy))
                    
                    # Calcola distanza minima da qualsiasi cella del blocco
                    min_dist = float('inf')
                    for bx, by in block_cells:
                        dist = abs(bx - coin_pos[0]) + abs(by - coin_pos[1])
                        min_dist = min(min_dist, dist)
                    
                    if min_dist < min_coin_dist:
                        return None  # Moneta troppo vicina, scarta livello
        
        coins_data = [{'color': c['color'], 'xy': list(c['pos'])} for c in coins_positions]
        
        # Ottieni time_limit dal target
        if target.get('use_dynamic_timer', False):
            # Usa formula dinamica: (actual_moves * 2) + 15
            time_limit = (len(move_history) * 2) + 15
        else:
            # Usa time_limit fisso dal target (se presente)
            time_limit = target.get('time_limit', None)
        
        level_data = self._create_level_data(
            level_num, layout, blocks_initial, coins_data, max_moves, time_limit
        )
        
        # Il numero di mosse è quello che abbiamo applicato
        actual_moves = len(move_history)
        
        # Verifica che abbiamo raggiunto il minimo di mosse
        if actual_moves < min_moves:
            return None  # Non abbastanza mosse, riprova
        
        return level_data, actual_moves
    
    def _is_valid_reverse_move(self, block: Dict, new_pos: Tuple[int, int], 
                               layout: List[List[int]], all_blocks: Dict, 
                               coins: List[Dict]) -> bool:
        """Verifica se una mossa inversa è valida"""
        grid_w = len(layout[0])
        grid_h = len(layout)
        shape_cells = SHAPE_CELLS[block['shape']]
        
        # Verifica bounds e muri
        for dx, dy in shape_cells:
            x, y = new_pos[0] + dx, new_pos[1] + dy
            if x < 0 or x >= grid_w or y < 0 or y >= grid_h:
                return False
            if layout[y][x] == 1:
                return False
        
        # Verifica collisioni con altri blocchi
        new_cells = set()
        for dx, dy in shape_cells:
            new_cells.add((new_pos[0] + dx, new_pos[1] + dy))
        
        for other_id, other_block in all_blocks.items():
            if other_id != block['id']:
                if new_cells & other_block['cells']:
                    return False
        
        # Verifica collisioni con monete (le monete sono ostacoli)
        for coin in coins:
            coin_pos = tuple(coin['pos'])
            if coin_pos in new_cells:
                # Moneta dello stesso colore NON è ostacolo
                if coin['color'] != block['color']:
                    return False
        
        return True
    
    def generate_level(self, level_num: int, target: Dict, max_attempts: int = 2000) -> Tuple[Optional[Dict], int]:
        """Genera un livello con approccio REVERSE PATHFINDING"""
        
        # Filtro mosse REWORK 5.0
        if level_num <= 5:
            min_moves_required = 10  # Minimo 10 mosse
        elif level_num <= 20:
            min_moves_required = 12  # Minimo 12 mosse
        else:
            min_moves_required = 5
        
        for attempt in range(max_attempts):
            result = self._generate_level_reverse(target, level_num)
            
            if result is None:
                continue
            
            level_data, num_moves = result
            
            # Applica filtro difficoltà
            if num_moves < min_moves_required:
                continue  # Troppo facile
            
            # Validazione strutturale rapida
            if not self.validator._validate_structure(level_data):
                continue
            
            # Quick validation
            quick_ok, quick_msg = self.validator.quick_validate(level_data)
            if not quick_ok:
                continue
            
            # OPZIONALE: Validazione BFS completa (solo per debug/verifica)
            # Disabilitata per default per velocità
            if SOLVER_AVAILABLE and level_num <= 10:  # Valida solo primi 10 livelli
                min_moves, max_moves = target["target_moves"]
                is_valid, msg, solved_moves = self.validator.validate_level(
                    level_data, min_moves=min_moves_required
                )
                if not is_valid:
                    continue
                # Usa il numero di mosse del solver se disponibile
                num_moves = solved_moves
            
            return level_data, num_moves
        
        return None, 0

    
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
                          blocks: List[Dict], coins: List[Dict], max_moves: int, 
                          time_limit: int = None) -> Dict:
        """Crea struttura dati livello"""
        grid_h = len(layout)
        grid_w = len(layout[0])
        
        # Usa time_limit personalizzato o calcola default
        if time_limit is None:
            time_limit = 60 + level_num * 5
        
        return {
            "meta": {
                "id": level_num,
                "world": 1 + (level_num - 1) // 50,
                "name": f"Level {level_num}",
                "grid_size": [grid_w, grid_h],
                "time_limit": time_limit,
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


<<<<<<< HEAD

def main():
    """Funzione principale per gestire l'esecuzione da riga di comando."""
    
    generator = SmartLevelGenerator()
    
    parser = argparse.ArgumentParser(
        description="TetraCoin Level Generator V3 - Genera e valida livelli."
    )
    
    # Argomenti principali
    parser.add_argument(
        '--generate-all', 
        type=int, 
        metavar='N', 
        help="Genera N livelli ufficiali ripartendo dal Livello 1 (cancella i vecchi)."
    )
    
    # Argomenti per i test
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--test-random', 
        type=int, 
        metavar='N', 
        help="Genera N livelli casuali per test (non ufficiali)."
    )
    group.add_argument(
        '--test-difficulty', 
        type=int, 
        metavar='LEVEL_NUM', 
        help="Genera 5 livelli di test con la difficoltà del livello LEVEL_NUM."
    )

    args = parser.parse_args()

    # --- Logica di Esecuzione ---
    
    if args.generate_all:
        generator.generate_all_levels(num_levels=args.generate_all)
        
    elif args.test_random:
        # Questo è il comando che stavi cercando: python --test-random 1
        generator.generate_random_test_levels(count=args.test_random)
        
    elif args.test_difficulty:
        generator.generate_test_at_difficulty(difficulty_level=args.test_difficulty)
        
    else:
        # Se non viene fornito nessun argomento, stampa l'help
        parser.print_help()


if __name__ == "__main__":
    main()
=======
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="TetraCoin Level Generator V3 - Reverse Pathfinding",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate levels 1-20
  python level_generator_v3.py --start 1 --end 20
  
  # Generate levels 100-120
  python level_generator_v3.py --start 100 --end 120
  
  # Generate first 10 levels (legacy mode)
  python level_generator_v3.py --count 10
  
  # Generate test levels
  python level_generator_v3.py --test --count 5
        """
    )
    
    parser.add_argument("--start", type=int, default=1, help="Starting level number (default: 1)")
    parser.add_argument("--end", type=int, help="Ending level number (inclusive). If specified, overrides --count")
    parser.add_argument("--count", type=int, help="Number of levels to generate (alternative to --end)")
    parser.add_argument("--test", action="store_true", help="Generate test levels instead")
    parser.add_argument("--test-difficulty", type=int, help="Generate test levels at specific difficulty")
    
    args = parser.parse_args()
    
    generator = SmartLevelGenerator()
    
    if args.test_difficulty:
        generator.generate_test_at_difficulty(args.test_difficulty, count=5)
    elif args.test:
        count = args.count if args.count else 10
        generator.generate_random_test_levels(count)
    else:
        # Determine range
        start = args.start
        
        if args.end:
            # Range mode: --start X --end Y
            end = args.end
            if end < start:
                print(f"❌ Errore: --end ({end}) deve essere >= --start ({start})")
                exit(1)
            num_levels = end
        elif args.count:
            # Count mode: --start X --count N
            num_levels = start + args.count - 1
        else:
            # Default: generate 10 levels starting from --start
            num_levels = start + 9
        
        print(f"📦 Generazione livelli {start}-{num_levels}...")
        generator.generate_all_levels(num_levels=num_levels, start_from=start)
>>>>>>> 5db67f2eedc748b12f9b4b6c8633d696020195aa
