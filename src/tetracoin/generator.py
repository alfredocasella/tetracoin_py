"""
Tetracoin Grid Generator.
Generates valid, solvable levels based on physics mechanics.
"""
import random
from typing import List, Tuple, Optional, Dict
import copy

from src.tetracoin.spec import GridState, EntityType, ColorType, Entity, Coin, PiggyBank, Obstacle, FixedBlock
from src.tetracoin.validation import ValidationEngine
from src.tetracoin.validation import ValidationEngine
from src.tetracoin.coin_placer import CoinPlacer
from src.tetracoin.flow_control import FlowControlObstacleAdder

class TetracoinGridGenerator:
    """
    Generator for physics-based puzzle grids.
    """
    
    def __init__(
        self,
        difficulty: int,
        grid_width: int,
        grid_height: int,
        num_coins: int,
        num_piggybanks: int,
        seed: Optional[int] = None
    ):
        self.difficulty = max(1, min(10, difficulty))
        self.width = grid_width
        self.height = grid_height
        self.num_coins = num_coins
        self.num_piggybanks = num_piggybanks
        self.seed = seed
        
        if seed is not None:
            random.seed(seed)
            
    def generate(self, max_attempts: int = 50) -> Optional[GridState]:
        """Generate a valid grid."""
        
        for attempt in range(max_attempts):
            grid = self._attempt_generation()
            if grid:
                return grid
                
        return None
        
    def _attempt_generation(self) -> Optional[GridState]:
        """Single generation attempt."""
        
        # FASE 1: Grid Initialization
        grid = GridState(rows=self.height, cols=self.width)
        
        # FASE 2: PiggyBanks
        # Place them at the bottom usually, or scattered?
        # For gravity puzzles, bottom is standard.
        occupied_cols = set()
        piggybanks = []
        
        available_cols = list(range(self.width))
        random.shuffle(available_cols)
        
        # Assign colors to piggybanks
        colors = [ColorType.RED, ColorType.BLUE, ColorType.GREEN, ColorType.YELLOW, ColorType.PURPLE]
        
        for i in range(self.num_piggybanks):
            if not available_cols:
                break
            
            col = available_cols.pop()
            row = self.height - 1
            color = colors[i % len(colors)]
            
            pb = PiggyBank(
                id=f"pb_{i}",
                row=row,
                col=col,
                color=color,
                capacity=5 # Default capacity
            )
            grid.entities.append(pb)
            piggybanks.append(pb)
            occupied_cols.add(col)
            
        # FASE 3: Coins
        # Use CoinPlacer to strategically place coins
        placer = CoinPlacer(rng=random)
        if not placer.place_coins_strategic(grid, self.num_coins, self.difficulty):
            return None
            
        # FASE 4: Obstacles / Flow Control
        # Use FlowControlObstacleAdder to manage supports, deflectors, etc.
        obstacle_adder = FlowControlObstacleAdder(rng=random)
        grid = obstacle_adder.add_obstacles(grid, self.difficulty)
            
        # FASE 5: Validation
        # Check if all coins can reach their piggybanks
        # We rely on reachability check. Simulating full solution requires player interaction logic
        # which is not yet fully defined in the validation engine.
        if not ValidationEngine.check_reachability(grid):
            return None
            
        # Full validation: Check if solvable
        # Limit moves based on difficulty?
        max_depth = 5 + self.difficulty * 2 # Scopes: 7 to 25 moves
        solution = ValidationEngine.find_solution(grid, max_moves=max_depth)
        
        if not solution:
            return None # Unsolvable within bounds
            
        return grid
