"""
Tetracoin Solver Module.
Implements a BFS solver for the physics-based Tetracoin puzzle.
"""
from dataclasses import dataclass, field, replace
from typing import Tuple, List, FrozenSet, Dict, Optional, Set
from collections import deque
import copy

from src.tetracoin.spec import (
    GridState, EntityType, ColorType, PhysicsEngine, Entity, 
    Coin, PiggyBank, Obstacle, FixedBlock, Support, Deflector, Gateway, Trap
)

MoveDirection = str # "UP", "DOWN", "LEFT", "RIGHT"

@dataclass(frozen=True)
class Move:
    entity_id: str
    direction: MoveDirection
    
    def __repr__(self):
        return f"{self.entity_id}->{self.direction}"

@dataclass(frozen=True)
class GameStateData:
    """Immutable representation of the grid for hashing/visited checks."""
    # We flatten the grid or store entity states. 
    # Key state: Entity positions and PiggyBank counts.
    # We can use a frozenset of (id, r, c, type, color, etc) or just (id, r, c).
    # Since blocks don't change distinctness, (id, r, c) is enough if ids are unique?
    # PiggyBanks need (id, count).
    entity_positions: FrozenSet[Tuple[str, int, int]]
    piggybank_counts: FrozenSet[Tuple[str, int]]
    
    def __hash__(self):
        return hash((self.entity_positions, self.piggybank_counts))
    
    def __eq__(self, other):
        if not isinstance(other, GameStateData): return False
        return (self.entity_positions == other.entity_positions and 
                self.piggybank_counts == other.piggybank_counts)

class GameState:
    """
    Wrapper around GridState to provide solver logic (valid moves, is_winning).
    Maintains the 'Mutable' GridState internally for Physics simulation, 
    but provides immutable hash through 'data' property.
    """
    def __init__(self, grid: GridState, moves: Tuple[Move, ...] = ()):
        self.grid = grid
        self.moves = moves
        self._hash_cache = None
        
    @property
    def data(self) -> GameStateData:
        if self._hash_cache is None:
            # Build immutable representation
            pos_list = []
            pb_list = []
            for e in self.grid.entities:
                if not e.is_collected:
                    pos_list.append((e.id, e.row, e.col))
                if e.type == EntityType.PIGGYBANK:
                    pb = e # type: PiggyBank
                    pb_list.append((e.id, pb.current_count))
            
            # Sort to ensure consistency? FrozenSet handles order independence.
            self._hash_cache = GameStateData(
                entity_positions=frozenset(pos_list),
                piggybank_counts=frozenset(pb_list)
            )
        return self._hash_cache

    def __hash__(self):
        return hash(self.data)

    def __eq__(self, other):
        if not isinstance(other, GameState): return False
        return self.data == other.data
        
    def is_winning(self) -> bool:
        """Check if all coins are collected."""
        # Condition: No reachable coins left on grid? 
        # Or PiggyBanks full? Or specific target?
        # Standard: All coins collected.
        coins = [e for e in self.grid.entities if e.type == EntityType.COIN and not e.is_collected]
        return len(coins) == 0

    def get_valid_moves(self) -> List[Move]:
        """
        Identify all valid moves.
        A move is: Slide a movable entity (Obstacle, Deflector, Support) to an adjacent empty cell.
        """
        valid_moves = []
        
        # Identify movable entities. FixedBlock and PiggyBank are static. 
        # Coins are moved by gravity (Physics), usually not by player directly in this genre, 
        # UNLESS the puzzle is about sliding coins. 
        # Let's assume for now: Player moves BLOCKS (Obstacle, Deflector, Support).
        movable_types = (EntityType.OBSTACLE, EntityType.DEFLECTOR, EntityType.SUPPORT)
        
        directions = [("UP", -1, 0), ("DOWN", 1, 0), ("LEFT", 0, -1), ("RIGHT", 0, 1)]
        
        for e in self.grid.entities:
            if e.is_collected: continue
            if e.type in movable_types:
                # Try all 4 directions
                for d_name, dr, dc in directions:
                    nr, nc = e.row + dr, e.col + dc
                    if self.grid.is_valid_pos(nr, nc) and self.grid.is_empty(nr, nc):
                        valid_moves.append(Move(e.id, d_name))
        
        return valid_moves

    def apply_move(self, move: Move) -> 'GameState':
        """
        Apply a move and run physics simulation until stable.
        Returns a NEW GameState.
        """
        # 1. Deep Copy
        new_grid_state = copy.deepcopy(self.grid)
        
        # 2. Apply Player Move
        # Find entity
        entity = next((e for e in new_grid_state.entities if e.id == move.entity_id), None)
        if entity:
            dr, dc = 0, 0
            if move.direction == "UP": dr = -1
            elif move.direction == "DOWN": dr = 1
            elif move.direction == "LEFT": dc = -1
            elif move.direction == "RIGHT": dc = 1
            
            # Move blindly (validation was in get_valid_moves, but check again?)
            # Logic: Teleport to new pos
            entity.row += dr
            entity.col += dc
            
        # 3. Process Physics (Gravity/Simulation)
        # Run until settled or max ticks
        max_ticks = 100
        stable = False
        
        for _ in range(max_ticks):
            prev_snapshot = str([(e.id, e.row, e.col, e.is_collected) for e in new_grid_state.entities])
            new_grid_state, events = PhysicsEngine.update(new_grid_state)
            curr_snapshot = str([(e.id, e.row, e.col, e.is_collected) for e in new_grid_state.entities])
            
            if prev_snapshot == curr_snapshot:
                stable = True
                break
                
        # 4. Return new state
        new_moves = self.moves + (move,)
        return GameState(new_grid_state, new_moves)

class TetracoinSolver:
    @staticmethod
    def solve_bfs(initial_grid: GridState, max_depth: int = 20) -> Tuple[bool, int, List[Move]]:
        """
        BFS Solver.
        Returns: (found, steps, moves)
        """
        # 0. Settle initial grid (simulate gravity/interactions without player input)
        # We need a copy because we don't want to mutate the input grid passed by caller
        settled_grid = copy.deepcopy(initial_grid)
        max_ticks = 1000
        for _ in range(max_ticks):
            prev_snapshot = str([(e.id, e.row, e.col, e.is_collected) for e in settled_grid.entities])
            settled_grid, _ = PhysicsEngine.update(settled_grid)
            curr_snapshot = str([(e.id, e.row, e.col, e.is_collected) for e in settled_grid.entities])
            if prev_snapshot == curr_snapshot:
                break
                
        initial_state = GameState(settled_grid)
        
        if initial_state.is_winning():
            return True, 0, []
            
        queue = deque([initial_state])
        visited: Set[GameStateData] = {initial_state.data}
        
        while queue:
            state = queue.popleft()
            
            if len(state.moves) >= max_depth:
                continue
                
            for move in state.get_valid_moves():
                next_state = state.apply_move(move)
                
                if next_state.data not in visited:
                    if next_state.is_winning():
                        return True, len(next_state.moves), list(next_state.moves)
                        
                    visited.add(next_state.data)
                    queue.append(next_state)
                    
        return False, 0, []
