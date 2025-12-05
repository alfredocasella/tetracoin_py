"""
Coin Placement Logic Module.
Centralizes all logic for strategic coin positioning based on difficulty.
"""
import random
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum

from src.tetracoin.spec import GridState, EntityType, ColorType, Coin, PiggyBank

class DifficultyLevel(str, Enum):
    EASY = "EASY"       # 1-3
    MEDIUM = "MEDIUM"   # 4-6
    HARD = "HARD"       # 7-8
    EXPERT = "EXPERT"   # 9-10
    
    @staticmethod
    def from_int(level: int) -> 'DifficultyLevel':
        if level <= 3: return DifficultyLevel.EASY
        if level <= 6: return DifficultyLevel.MEDIUM
        if level <= 8: return DifficultyLevel.HARD
        return DifficultyLevel.EXPERT

class CoinPlacer:
    """
    Handles strategic placement of coins on the game grid.
    """
    
    def __init__(self, rng=None):
        self.rng = rng if rng else random
        
    def place_coins_strategic(self, grid: GridState, num_coins: int, difficulty: int) -> bool:
        """
        Main entry point for placing coins.
        params:
            grid: GridState object (will be modified in-place)
            num_coins: Total number of coins to place
            difficulty: Integer 1-10
        returns: True if successful, False if failed to place all coins
        """
        diff_level = DifficultyLevel.from_int(difficulty)
        piggybanks = [e for e in grid.entities if e.type == EntityType.PIGGYBANK]
        
        if not piggybanks:
            return False # Cannot place coins without piggybanks
            
        # 1. Distribute coins among piggybank colors
        coin_definitions = self._distribute_coins_to_colors(num_coins, piggybanks)
        
        # 2. Select strategy based on difficulty
        if diff_level == DifficultyLevel.EASY:
            return self._place_easy(grid, coin_definitions, piggybanks)
        elif diff_level == DifficultyLevel.MEDIUM:
            return self._place_medium(grid, coin_definitions, piggybanks)
        elif diff_level == DifficultyLevel.HARD:
            return self._place_hard(grid, coin_definitions, piggybanks)
        else:
            return self._place_expert(grid, coin_definitions, piggybanks)

    def _distribute_coins_to_colors(self, num_coins: int, piggybanks: List[PiggyBank]) -> List[ColorType]:
        """Assigns a color to each coin to be placed, ensuring piggybanks have capacity."""
        coins_needed = num_coins
        coins_per_piggy = coins_needed // len(piggybanks)
        remainder = coins_needed % len(piggybanks)
        
        coin_definitions = []
        for i, pb in enumerate(piggybanks):
            count = coins_per_piggy + (1 if i < remainder else 0)
            # Update piggybank capacity if needed (though generator usually sets this)
            pb.capacity = max(pb.capacity, count) 
            for _ in range(count):
                coin_definitions.append(pb.color)
                
        self.rng.shuffle(coin_definitions)
        return coin_definitions

    def _get_empty_spots(self, grid: GridState) -> Dict[int, List[Tuple[int, int]]]:
        """Returns empty spots grouped by column."""
        spots = {c: [] for c in range(grid.cols)}
        # Limit placement height to avoid placing too high? Generator used height-2
        upper_limit = grid.rows - 1 # Use all rows except bottom (piggybanks)
        
        for c in range(grid.cols):
            for r in range(upper_limit):
                if grid.is_empty(r, c):
                    spots[c].append((r, c))
            self.rng.shuffle(spots[c])
        return spots

    def _place_easy(self, grid: GridState, coin_defs: List[ColorType], piggybanks: List[PiggyBank]) -> bool:
        """
        EASY STRATEGY:
        - Prioritize direct vertical access (same column).
        - Avoid tight clusters?
        """
        empty_spots = self._get_empty_spots(grid)
        piggies_by_color = _map_piggies(piggybanks)
        
        return self._place_generic(grid, coin_defs, piggies_by_color, empty_spots, 
                                   allow_adjacent=False, allow_random=False)

    def _place_medium(self, grid: GridState, coin_defs: List[ColorType], piggybanks: List[PiggyBank]) -> bool:
        """
        MEDIUM STRATEGY:
        - Prioritize same column.
        - Allow adjacent columns (requires simple slide).
        """
        empty_spots = self._get_empty_spots(grid)
        piggies_by_color = _map_piggies(piggybanks)
        
        return self._place_generic(grid, coin_defs, piggies_by_color, empty_spots, 
                                   allow_adjacent=True, allow_random=False)

    def _place_hard(self, grid: GridState, coin_defs: List[ColorType], piggybanks: List[PiggyBank]) -> bool:
        """
        HARD STRATEGY:
        - Mix of direct and offset.
        - Encourage some stacking or riskier placement (higher up?).
        """
        empty_spots = self._get_empty_spots(grid)
        piggies_by_color = _map_piggies(piggybanks)
        
        # In hard mode, we might shuffle prioritization or force some "bad" columns 
        # that require deflection. For now, allowing random fallback simulates this.
        return self._place_generic(grid, coin_defs, piggies_by_color, empty_spots, 
                                   allow_adjacent=True, allow_random=True)

    def _place_expert(self, grid: GridState, coin_defs: List[ColorType], piggybanks: List[PiggyBank]) -> bool:
        """
        EXPERT STRATEGY:
        - Aggressive usage of difficult spots.
        - High randomness in column selection (requires solving deflection).
        """
        empty_spots = self._get_empty_spots(grid)
        piggies_by_color = _map_piggies(piggybanks)
        
        return self._place_generic(grid, coin_defs, piggies_by_color, empty_spots, 
                                   allow_adjacent=True, allow_random=True, prioritize_direct=False)

    def _place_generic(self, grid: GridState, coin_defs: List[ColorType], 
                       piggies_by_color: Dict[ColorType, List[PiggyBank]],
                       empty_spots_by_col: Dict[int, List[Tuple[int, int]]],
                       allow_adjacent: bool = False,
                       allow_random: bool = False,
                       prioritize_direct: bool = True) -> bool:
        
        coin_id = len([e for e in grid.entities if e.type == EntityType.COIN])
        
        for color in coin_defs:
            placed = False
            targets = piggies_by_color.get(color, [])
            self.rng.shuffle(targets)
            
            # 1. Direct Column Attempt
            if prioritize_direct:
                for target_pb in targets:
                    if self._try_place_in_col(grid, color, target_pb.col, empty_spots_by_col, coin_id):
                        placed = True
                        coin_id += 1
                        break
            
            # 2. Adjacent Column Attempt
            if not placed and allow_adjacent:
                for target_pb in targets:
                    # Try left then right
                    neighbors = [target_pb.col - 1, target_pb.col + 1]
                    self.rng.shuffle(neighbors)
                    for ncol in neighbors:
                         if 0 <= ncol < grid.cols:
                            if self._try_place_in_col(grid, color, ncol, empty_spots_by_col, coin_id):
                                placed = True
                                coin_id += 1
                                break
                    if placed: break
            
            # 3. Random/Any Column Attempt
            if not placed and (allow_random or not prioritize_direct):
                 # Try finding ANY spot
                 all_cols = list(range(grid.cols))
                 self.rng.shuffle(all_cols)
                 for col in all_cols:
                     if self._try_place_in_col(grid, color, col, empty_spots_by_col, coin_id):
                        placed = True
                        coin_id += 1
                        break
            
            if not placed:
                return False # Could not place this coin
                
        return True

    def _try_place_in_col(self, grid: GridState, color: ColorType, col: int, 
                          spots: Dict[int, List[Tuple[int, int]]], cid: int) -> bool:
        if spots.get(col):
            r, c = spots[col].pop() # Use from list
            coin = Coin(id=f"c_{cid}", row=r, col=c, color=color)
            grid.entities.append(coin)
            return True
        return False

def _map_piggies(piggies: List[PiggyBank]) -> Dict[ColorType, List[PiggyBank]]:
    m = {}
    for p in piggies:
        if p.color not in m: m[p.color] = []
        m[p.color].append(p)
    return m
