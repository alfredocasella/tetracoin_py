#!/usr/bin/env python3
"""
Script per applicare le modifiche al level_generator_v3.py
Integra il BFS e corregge il numero di blocchi per L4-10
"""

import re

# Leggi il file
with open('scripts/level_generator_v3.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Modifica 1: Sostituisci validate_level per usare BFS integrato
old_validate = '''    def validate_level(self, level_data: Dict, min_moves: int = 5) -> Tuple[bool, str, int]:
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
        
        return True, "Valid", num_moves'''

new_validate = '''    def validate_level(self, level_data: Dict, min_moves: int = 5) -> Tuple[bool, str, int]:
        """Validazione completa con BFS integrato"""
        
        # Prima: validazione rapida
        quick_ok, quick_msg = self.quick_validate(level_data)
        if not quick_ok:
            return False, f"Quick check failed: {quick_msg}", 0
        
        # Poi: validazione strutturale
        if not self._validate_structure(level_data):
            return False, "Invalid structure", 0
        
        # Infine: BFS solver integrato (costoso)
        is_solvable, num_moves = self.is_solvable(level_data)
        
        if not is_solvable:
            return False, "Level is not solvable", 0
        
        if num_moves < min_moves:
            return False, f"Too easy: only {num_moves} moves", num_moves
        
        return True, "Valid", num_moves'''

content = content.replace(old_validate, new_validate)

# Modifica 2: Correggi numero blocchi L4-10
old_blocks = '''                "blocks": min(3, 2 + (i - 4) // 3),  # Crescita graduale'''
new_blocks = '''                "blocks": 4,  # Min 4 blocchi dal L4 (GDD 4.0)'''

content = content.replace(old_blocks, new_blocks)

# Aggiungi i metodi BFS dopo _validate_structure
bfs_methods = '''
    
    def is_solvable(self, level_data: Dict, max_moves: int = 100) -> Tuple[bool, int]:
        """Verifica se un livello è risolvibile usando BFS"""
        initial_state = self._create_game_state(level_data)
        if self._is_win_state(initial_state):
            return True, 0
        
        queue = deque([(initial_state, 0)])
        visited = set()
        visited.add(self._state_to_hash(initial_state))
        
        states_explored = 0
        max_states = 10000
        
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
'''

# Trova dove inserire i metodi BFS (dopo _validate_structure)
insert_marker = '''        return True


class SmartLevelGenerator:'''

content = content.replace(insert_marker, f'''        return True
{bfs_methods}

class SmartLevelGenerator:''')

# Salva il file modificato
with open('scripts/level_generator_v3.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Modifiche applicate con successo!")
print("   - validate_level ora usa BFS integrato")
print("   - L4-10 ora hanno 4 blocchi (GDD 4.0)")
print("   - Metodi BFS aggiunti alla classe LevelValidator")
