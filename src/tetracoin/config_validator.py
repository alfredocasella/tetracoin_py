from typing import List, Tuple, Set, Optional
from dataclasses import dataclass
from collections import deque

@dataclass
class ValidationResult:
    """Risultato della validazione con flag di successo e lista errori."""
    is_valid: bool
    errors: List[str]
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

class TetracoinConfigValidator:
    """
    Validatore centralizzato per configurazioni Tetracoin.
    
    Responsabilità:
    - Verificare raggiungibilità di tutte le monete
    - Rilevare configurazioni banali (troppo facili)
    - Rilevare configurazioni impossibili
    - Identificare perdite ingiuste di monete
    - Segnalare layout noiosi o degeneri
    """
    
    def __init__(self, 
                 min_path_length: int = 3,
                 max_trivial_distance: int = 2,
                 min_obstacles_ratio: float = 0.05,
                 max_obstacles_ratio: float = 0.4):
        """
        Args:
            min_path_length: Lunghezza minima del percorso per evitare banalità
            max_trivial_distance: Distanza massima per considerare una moneta "troppo vicina"
            min_obstacles_ratio: Rapporto minimo ostacoli/celle totali
            max_obstacles_ratio: Rapporto massimo ostacoli/celle totali
        """
        self.min_path_length = min_path_length
        self.max_trivial_distance = max_trivial_distance
        self.min_obstacles_ratio = min_obstacles_ratio
        self.max_obstacles_ratio = max_obstacles_ratio
    
    def validate(self, grid: dict) -> ValidationResult:
        """
        Valida una configurazione di gioco completa.
        
        Args:
            grid: Dizionario con chiavi:
                - 'width': int
                - 'height': int
                - 'player_start': Tuple[int, int]
                - 'coins': List[Tuple[int, int]]
                - 'obstacles': List[Tuple[int, int]]
        
        Returns:
            ValidationResult con is_valid=True se passa tutti i controlli
        """
        errors = []
        warnings = []
        
        # 1. Validazione struttura base
        structure_errors = self._validate_structure(grid)
        if structure_errors:
            # Se la struttura manca, non possiamo procedere
            return ValidationResult(False, structure_errors, warnings)
        
        # 2. Validazione bounds
        bounds_errors = self._validate_bounds(grid)
        errors.extend(bounds_errors)
        
        # 3. Validazione collisioni
        collision_errors = self._validate_collisions(grid)
        errors.extend(collision_errors)
        
        # 4. Validazione raggiungibilità
        reachability_errors = self._validate_reachability(grid)
        errors.extend(reachability_errors)
        
        # 5. Validazione banalità
        triviality_warnings = self._validate_triviality(grid)
        warnings.extend(triviality_warnings)
        
        # 6. Validazione layout
        layout_warnings = self._validate_layout(grid)
        warnings.extend(layout_warnings)
        
        # 7. Validazione perdite ingiuste
        unfair_errors = self._validate_unfair_coin_loss(grid)
        errors.extend(unfair_errors)
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)

    # 2. Metodi di Validazione Interni

    def _validate_structure(self, grid: dict) -> List[str]:
        """Verifica che il dizionario grid contenga tutte le chiavi necessarie."""
        errors = []
        required_keys = ['width', 'height', 'player_start', 'coins', 'obstacles']
        
        for key in required_keys:
            if key not in grid:
                errors.append(f"Chiave mancante nella configurazione: '{key}'")
        
        if not errors:
            # Verifica tipi
            if not isinstance(grid['width'], int) or grid['width'] <= 0:
                errors.append(f"'width' deve essere un intero positivo, ricevuto: {grid['width']}")
            
            if not isinstance(grid['height'], int) or grid['height'] <= 0:
                errors.append(f"'height' deve essere un intero positivo, ricevuto: {grid['height']}")
            
            if not isinstance(grid['player_start'], (tuple, list)) or len(grid['player_start']) != 2:
                errors.append(f"'player_start' deve essere una tupla (x, y), ricevuto: {grid['player_start']}")
            
            if not isinstance(grid['coins'], list):
                errors.append(f"'coins' deve essere una lista, ricevuto: {type(grid['coins'])}")
            
            if not isinstance(grid['obstacles'], list):
                errors.append(f"'obstacles' deve essere una lista, ricevuto: {type(grid['obstacles'])}")
        
        return errors

    def _validate_bounds(self, grid: dict) -> List[str]:
        """Verifica che tutte le posizioni siano dentro i limiti della griglia."""
        errors = []
        width = grid['width']
        height = grid['height']
        
        def is_out_of_bounds(pos: Tuple[int, int]) -> bool:
            x, y = pos
            return x < 0 or x >= width or y < 0 or y >= height
        
        # Controlla player_start
        if is_out_of_bounds(grid['player_start']):
            errors.append(f"player_start {grid['player_start']} fuori dai limiti ({width}x{height})")
        
        # Controlla coins
        for i, coin in enumerate(grid['coins']):
            if is_out_of_bounds(coin):
                errors.append(f"Coin {i} alla posizione {coin} fuori dai limiti ({width}x{height})")
        
        # Controlla obstacles
        for i, obs in enumerate(grid['obstacles']):
            if is_out_of_bounds(obs):
                errors.append(f"Obstacle {i} alla posizione {obs} fuori dai limiti ({width}x{height})")
        
        return errors

    def _validate_collisions(self, grid: dict) -> List[str]:
        """Verifica che non ci siano sovrapposizioni tra elementi."""
        errors = []
        
        player_pos = tuple(grid['player_start'])
        coins_set = set(tuple(c) for c in grid['coins'])
        obstacles_set = set(tuple(o) for o in grid['obstacles'])
        
        # Player su ostacolo
        if player_pos in obstacles_set:
            errors.append(f"Player start {player_pos} collide con un ostacolo")
        
        # Player su moneta (warning, non errore critico)
        if player_pos in coins_set:
            errors.append(f"Player start {player_pos} collide con una moneta (raccolta istantanea)")
        
        # Monete su ostacoli
        coin_obstacle_overlap = coins_set & obstacles_set
        if coin_obstacle_overlap:
            errors.append(f"Monete e ostacoli si sovrappongono in: {coin_obstacle_overlap}")
        
        # Monete duplicate
        if len(grid['coins']) != len(coins_set):
            errors.append(f"Monete duplicate rilevate: {len(grid['coins'])} totali, {len(coins_set)} uniche")
        
        # Ostacoli duplicati
        if len(grid['obstacles']) != len(obstacles_set):
            errors.append(f"Ostacoli duplicati rilevati: {len(grid['obstacles'])} totali, {len(obstacles_set)} unici")
        
        return errors

    def _validate_reachability(self, grid: dict) -> List[str]:
        """Verifica che tutte le monete siano raggiungibili dal player_start."""
        errors = []
        
        if not grid['coins']:
            errors.append("Nessuna moneta presente nella configurazione")
            return errors
        
        obstacles_set = set(tuple(o) for o in grid['obstacles'])
        
        for i, coin in enumerate(grid['coins']):
            coin_tuple = tuple(coin)
            if not self._coin_has_valid_path(grid, coin_tuple, obstacles_set):
                errors.append(f"Moneta {i} alla posizione {coin_tuple} non è raggiungibile")
        
        return errors

    def _coin_has_valid_path(self, grid: dict, coin: Tuple[int, int], obstacles_set: Set) -> bool:
        """
        BFS per verificare se esiste un percorso dal player_start alla moneta.
        
        Returns:
            True se la moneta è raggiungibile, False altrimenti
        """
        start = tuple(grid['player_start'])
        target = coin
        
        if start == target:
            return True
        
        width = grid['width']
        height = grid['height']
        
        queue = deque([start])
        visited = {start}
        
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        while queue:
            x, y = queue.popleft()
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                next_pos = (nx, ny)
                
                # Controlla bounds
                if nx < 0 or nx >= width or ny < 0 or ny >= height:
                    continue
                
                # Controlla ostacoli
                if next_pos in obstacles_set:
                    continue
                
                # Controlla già visitato
                if next_pos in visited:
                    continue
                
                # Trovato target
                if next_pos == target:
                    return True
                
                visited.add(next_pos)
                queue.append(next_pos)
        
        return False

    def _validate_triviality(self, grid: dict) -> List[str]:
        """Rileva configurazioni troppo facili o banali."""
        warnings = []
        
        if not grid.get('coins'):
            return warnings

        # Controlla se tutte le monete sono troppo vicine
        if self._is_trivial(grid):
            warnings.append("Configurazione banale: tutte le monete sono troppo vicine al player")
        
        # Controlla se non ci sono ostacoli sufficienti
        total_cells = grid['width'] * grid['height']
        obstacle_ratio = len(grid['obstacles']) / total_cells
        
        if obstacle_ratio < self.min_obstacles_ratio:
            warnings.append(f"Pochi ostacoli: {obstacle_ratio:.2%} (minimo consigliato: {self.min_obstacles_ratio:.2%})")
        
        # Controlla percorso troppo corto
        if grid['coins']:
            shortest_path = self._get_shortest_path_length(grid, tuple(grid['coins'][0]))
            if shortest_path is not None and shortest_path < self.min_path_length:
                warnings.append(f"Percorso troppo corto verso prima moneta: {shortest_path} celle (minimo: {self.min_path_length})")
        
        return warnings

    def _is_trivial(self, grid: dict) -> bool:
        """Verifica se tutte le monete sono raggiungibili con distanza Manhattan minima."""
        player_pos = grid['player_start']
        
        for coin in grid['coins']:
            manhattan_dist = abs(coin[0] - player_pos[0]) + abs(coin[1] - player_pos[1])
            if manhattan_dist > self.max_trivial_distance:
                return False
        
        return True

    def _get_shortest_path_length(self, grid: dict, target: Tuple[int, int]) -> Optional[int]:
        """Calcola la lunghezza del percorso più breve verso un target usando BFS."""
        start = tuple(grid['player_start'])
        
        if start == target:
            return 0
        
        width = grid['width']
        height = grid['height']
        obstacles_set = set(tuple(o) for o in grid['obstacles'])
        
        queue = deque([(start, 0)])
        visited = {start}
        
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        while queue:
            (x, y), dist = queue.popleft()
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                next_pos = (nx, ny)
                
                if nx < 0 or nx >= width or ny < 0 or ny >= height:
                    continue
                
                if next_pos in obstacles_set or next_pos in visited:
                    continue
                
                if next_pos == target:
                    return dist + 1
                
                visited.add(next_pos)
                queue.append((next_pos, dist + 1))
        
        return None

    def _validate_layout(self, grid: dict) -> List[str]:
        """Rileva layout noiosi o degeneri."""
        warnings = []
        
        total_cells = grid['width'] * grid['height']
        obstacle_ratio = len(grid['obstacles']) / total_cells
        
        # Troppi ostacoli
        if obstacle_ratio > self.max_obstacles_ratio:
            warnings.append(f"Troppi ostacoli: {obstacle_ratio:.2%} (massimo consigliato: {self.max_obstacles_ratio:.2%})")
        
        # Griglia troppo piccola
        if total_cells < 16:
            warnings.append(f"Griglia molto piccola: {grid['width']}x{grid['height']} = {total_cells} celle")
        
        # Tutte le monete in linea retta
        if self._all_coins_collinear(grid):
            warnings.append("Tutte le monete sono allineate (layout noioso)")
        
        # Nessuna moneta
        if len(grid['coins']) == 0:
            warnings.append("Nessuna moneta presente nel livello")
        
        return warnings

    def _all_coins_collinear(self, grid: dict) -> bool:
        """Verifica se tutte le monete sono sulla stessa riga o colonna."""
        if len(grid['coins']) <= 1:
            return False
        
        coins = grid['coins']
        
        # Controlla stessa riga
        same_row = all(c[1] == coins[0][1] for c in coins)
        
        # Controlla stessa colonna
        same_col = all(c[0] == coins[0][0] for c in coins)
        
        return same_row or same_col

    def _validate_unfair_coin_loss(self, grid: dict) -> List[str]:
        """
        Rileva situazioni dove raccogliere una moneta rende altre irraggiungibili.
        Questo è un controllo avanzato che simula la raccolta sequenziale.
        """
        errors = []
        
        if len(grid['coins']) <= 1:
            return errors
        
        # Per ogni moneta, simula la sua raccolta e verifica che le altre restino raggiungibili
        for i, coin_to_collect in enumerate(grid['coins']):
            # Crea configurazione temporanea con questa moneta come ostacolo
            # (simulando che il player si ferma lì)
            temp_obstacles = set(tuple(o) for o in grid['obstacles'])
            
            # Verifica che tutte le altre monete siano ancora raggiungibili
            # da questa posizione
            temp_grid = grid.copy()
            temp_grid['player_start'] = coin_to_collect
            
            for j, other_coin in enumerate(grid['coins']):
                if i == j:
                    continue
                
                if not self._coin_has_valid_path(temp_grid, tuple(other_coin), temp_obstacles):
                    errors.append(
                        f"Raccogliere moneta {i} a {tuple(coin_to_collect)} "
                        f"rende irraggiungibile moneta {j} a {tuple(other_coin)}"
                    )
        
        return errors
