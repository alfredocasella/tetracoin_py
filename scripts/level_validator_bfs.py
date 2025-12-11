# Level Validator con BFS Integrato - Da copiare in level_generator_v3.py

# Sostituisci la classe LevelValidator (linee 209-277) con questa versione:

class LevelValidator:
    """Valida i livelli generati con pre-validazione rapida e BFS integrato"""
    
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
        """Validazione completa con BFS integrato"""
        
        # Prima: validazione rapida
        quick_ok, quick_msg = self.quick_validate(level_data)
        if not quick_ok:
            return False, f"Quick check failed: {quick_msg}", 0
        
        # Poi: validazione strutturale
        if not self._validate_structure(level_data):
            return False, "Invalid structure", 0
        
        # Infine: BFS solver (costoso ma integrato)
        is_solvable, num_moves = self.is_solvable(level_data)
        
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
    
    def is_solvable(self, level_data: Dict, max_moves: int = 100) -> Tuple[bool, int]:
        """
        Verifica se un livello è risolvibile usando BFS
        
        Esplora tutti gli stati possibili del gioco fino a trovare uno stato vincente
        o esaurire le possibilità.
        
        Args:
            level_data: Dati del livello
            max_moves: Numero massimo di mosse da esplorare
            
        Returns:
            (is_solvable, num_moves): True se risolvibile, numero di mosse necessarie
        """
        # Crea stato iniziale
        initial_state = self._create_game_state(level_data)
        
        # Verifica se già vinto (non dovrebbe mai succedere)
        if self._is_win_state(initial_state):
            return True, 0
        
        # BFS
        queue = deque([(initial_state, 0)])  # (state, num_moves)
        visited = set()
        visited.add(self._state_to_hash(initial_state))
        
        states_explored = 0
        max_states = 10000  # Limite per evitare loop infiniti
        
        while queue and states_explored < max_states:
            current_state, num_moves = queue.popleft()
            states_explored += 1
            
            # Esplora tutte le mosse possibili
            for next_state in self._get_next_states(current_state, level_data['layout']):
                state_hash = self._state_to_hash(next_state)
                
                if state_hash in visited:
                    continue
                
                visited.add(state_hash)
                new_num_moves = num_moves + 1
                
                # Verifica se troppo lungo
                if new_num_moves > max_moves:
                    continue
                
                # Verifica condizione di vittoria
                if self._is_win_state(next_state):
                    return True, new_num_moves
                
                queue.append((next_state, new_num_moves))
        
        return False, 0
    
    def _create_game_state(self, level_data: Dict) -> Dict:
        """Crea lo stato iniziale del gioco"""
        state = {
            'blocks': {},  # {block_id: {'pos': (x,y), 'shape': str, 'color': str, 'counter': int}}
            'coins': set(),  # {(x, y, color), ...}
            'collected': {}  # {color: count}
        }
        
        # Inizializza blocchi
        for block in level_data['blocks']:
            block_id = block['id']
            state['blocks'][block_id] = {
                'pos': tuple(block['xy']),
                'shape': block['shape'],
                'color': block['color'],
                'counter': block['counter']
            }
            # Inizializza contatore monete raccolte
            if block['color'] not in state['collected']:
                state['collected'][block['color']] = 0
        
        # Inizializza monete
        for coin in level_data['coins']['static']:
            state['coins'].add((coin['xy'][0], coin['xy'][1], coin['color']))
        
        return state
    
    def _state_to_hash(self, state: Dict) -> Tuple:
        """Converte uno stato in una rappresentazione hashabile"""
        # Hash basato su: posizioni blocchi + monete rimanenti
        block_positions = tuple(sorted(
            (bid, bdata['pos']) for bid, bdata in state['blocks'].items()
        ))
        remaining_coins = tuple(sorted(state['coins']))
        return (block_positions, remaining_coins)
    
    def _is_win_state(self, state: Dict) -> bool:
        """Verifica se lo stato è vincente (tutti i blocchi hanno raccolto le loro monete)"""
        for block_id, block_data in state['blocks'].items():
            color = block_data['color']
            required = block_data['counter']
            collected = state['collected'].get(color, 0)
            if collected < required:
                return False
        return True
    
    def _get_next_states(self, state: Dict, layout: List[List[int]]) -> List[Dict]:
        """
        Genera tutti gli stati successivi possibili muovendo ogni blocco in ogni direzione
        
        Returns:
            Lista di nuovi stati
        """
        next_states = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # down, up, right, left
        
        grid_h = len(layout)
        grid_w = len(layout[0]) if grid_h > 0 else 0
        
        for block_id in list(state['blocks'].keys()):
            block = state['blocks'][block_id]
            
            for dx, dy in directions:
                new_pos = (block['pos'][0] + dx, block['pos'][1] + dy)
                
                # Verifica se la mossa è valida
                if self._is_valid_move(state, block_id, new_pos, layout, grid_w, grid_h):
                    # Crea nuovo stato
                    new_state = self._apply_move(state, block_id, new_pos)
                    next_states.append(new_state)
        
        return next_states
    
    def _is_valid_move(self, state: Dict, block_id: str, new_pos: Tuple[int, int],
                       layout: List[List[int]], grid_w: int, grid_h: int) -> bool:
        """Verifica se un blocco può muoversi in una nuova posizione"""
        block = state['blocks'][block_id]
        shape = block['shape']
        shape_cells = SHAPE_CELLS.get(shape, [(0, 0)])
        
        # Ottieni celle occupate da altri blocchi
        other_block_cells = set()
        for other_id, other_block in state['blocks'].items():
            if other_id != block_id:
                other_shape_cells = SHAPE_CELLS.get(other_block['shape'], [(0, 0)])
                for dx, dy in other_shape_cells:
                    other_block_cells.add((other_block['pos'][0] + dx, other_block['pos'][1] + dy))
        
        # Verifica ogni cella del blocco nella nuova posizione
        for dx, dy in shape_cells:
            cell_x = new_pos[0] + dx
            cell_y = new_pos[1] + dy
            
            # Verifica bounds
            if not (0 <= cell_x < grid_w and 0 <= cell_y < grid_h):
                return False
            
            # Verifica muri
            if layout[cell_y][cell_x] == 1:
                return False
            
            # Verifica collisione con altri blocchi
            if (cell_x, cell_y) in other_block_cells:
                return False
            
            # Verifica collisione con monete di colore diverso
            for coin_x, coin_y, coin_color in state['coins']:
                if (cell_x, cell_y) == (coin_x, coin_y):
                    if coin_color != block['color']:
                        return False  # Moneta di colore diverso blocca il movimento
        
        return True
    
    def _apply_move(self, state: Dict, block_id: str, new_pos: Tuple[int, int]) -> Dict:
        """
        Applica una mossa e crea un nuovo stato
        
        Gestisce:
        - Movimento del blocco
        - Raccolta monete
        - Rimozione blocco se ha raccolto tutte le sue monete
        """
        # Deep copy dello stato
        new_state = {
            'blocks': {bid: bdata.copy() for bid, bdata in state['blocks'].items()},
            'coins': state['coins'].copy(),
            'collected': state['collected'].copy()
        }
        
        # Muovi il blocco
        block = new_state['blocks'][block_id]
        block['pos'] = new_pos
        
        # Raccogli monete
        shape_cells = SHAPE_CELLS.get(block['shape'], [(0, 0)])
        coins_to_remove = set()
        
        for dx, dy in shape_cells:
            cell_x = new_pos[0] + dx
            cell_y = new_pos[1] + dy
            
            # Cerca monete in questa cella
            for coin in new_state['coins']:
                coin_x, coin_y, coin_color = coin
                if (cell_x, cell_y) == (coin_x, coin_y) and coin_color == block['color']:
                    coins_to_remove.add(coin)
                    new_state['collected'][block['color']] += 1
        
        # Rimuovi monete raccolte
        new_state['coins'] -= coins_to_remove
        
        # Rimuovi blocco se ha raccolto tutte le sue monete
        if new_state['collected'][block['color']] >= block['counter']:
            del new_state['blocks'][block_id]
        
        return new_state
