"""
Validation and Solver logic for Tetracoin grids.
Handles reachability checks and level solvability.
"""
from typing import List, Tuple, Set, Optional, Dict
from collections import deque
import copy

from src.tetracoin.spec import (
    GridState, EntityType, ColorType, PhysicsEngine, Entity, 
    Coin, PiggyBank, Obstacle, FixedBlock, Support, Deflector, Gateway, Trap
)
from src.tetracoin.solver import TetracoinSolver

class ValidationEngine:
    """Helper class for validating grid states."""

    @staticmethod
    def check_reachability(state: GridState) -> bool:
        """
        Check if ALL coins in the grid can theoretically reach a PiggyBank of matching color.
        This is a static reachability check (ignoring dynamic blocking by other coins for now,
        or assuming perfect play).
        
        Ideally, we simulate gravity for each coin in isolation to see if it hits a deadline or a valid target.
        """
        coins = [e for e in state.entities if e.type == EntityType.COIN]
        piggybanks = [e for e in state.entities if e.type == EntityType.PIGGYBANK]
        
        # Optimization: Map piggybanks by color
        piggies_by_color: Dict[ColorType, List[PiggyBank]] = {}
        for p in piggybanks:
            if p.color not in piggies_by_color:
                piggies_by_color[p.color] = []
            piggies_by_color[p.color].append(p)
            
        for coin in coins:
            # If coin color has no piggybanks, it's unreachable
            if coin.color not in piggies_by_color:
                return False
                
            # Perform a BFS/Simulation to see if this coin can reach any valid piggybank
            if not ValidationEngine._can_reach_target(state, coin, piggies_by_color[coin.color]):
                return False
                
        return True

    @staticmethod
    def _can_reach_target(state: GridState, coin: Coin, targets: List[PiggyBank]) -> bool:
        """
        Determine if a specific coin can reach any of the target piggybanks.
        We simulate possible paths: gravity + lateral slides.
        """
        # BFS state: (row, col)
        start_node = (coin.row, coin.col)
        queue = deque([start_node])
        visited = {start_node}
        
        target_positions = {(p.row, p.col) for p in targets}
        
        # We need a simplified view of the grid: barriers.
        # We treat other coins as temporary? For "Reachability" we usually assume 
        # other coins can be moved/collected. So we mainly check against FIXED OBSTACLES/WALLS.
        # But wait, coins stack. A coin might need another coin to stack on to slide?
        # Let's assume conservatively: Coins are obstacles? No, that's too strict. 
        # Let's assume Coins are transparent for reachability (can be removed), 
        # but FixedBlocks/Obstacles are permanent.
        
        # However, Obstacles deflect. 
        
        while queue:
            r, c = queue.popleft()
            
            # Check if this position satisfies a target (e.g. directly above a piggybank?)
            # Actually physics says: if we are at (r, c), and (r+1, c) is a piggybank, we enter it.
            # So if (r+1, c) is in target_positions, we are good.
            if (r + 1, c) in target_positions:
                # But wait, checking color match? passed targets list already filtered by color.
                return True
                
            # Possible Moves:
            # 1. Gravity (Down)
            down = (r + 1, c)
            if ValidationEngine._is_traversable(state, down[0], down[1], ignore_coins=True):
                if down not in visited:
                    visited.add(down)
                    queue.append(down)
            
            # 2. Interactions (Deflection / Slide)
            # If (r+1, c) is blocked by OBSTACLE or FIXED_BLOCK, we can slide Left/Right?
            # Or if it's blocked, we stop.
            # "Sand Fall" rule: if down is blocked, check down-left and down-right.
            
            # Check what is at (r+1, c)
            blocker = state.get_entity_at(r + 1, c)
            # We ignored coins in traversable check, but for deflection checks we need to know strictly about solids.
            # If we treat coins as transparent, we assume they clear out.
            # But if there is a FIXED obstacle/block, we can slide.
            
            if blocker and blocker.type in (
                EntityType.OBSTACLE, EntityType.FIXED_BLOCK, 
                EntityType.SUPPORT, EntityType.GATEWAY, EntityType.TRAP,
                EntityType.DEFLECTOR
            ):
                # Determine allowed slide directions
                allowed_slides = []
                
                if blocker.type == EntityType.DEFLECTOR:
                    # Deflector forces specific direction
                    direction = getattr(blocker, 'direction', 'LEFT')
                    allowed_slides.append(direction)
                else:
                    # Standard blocks allow "Sand Fall" (both ways)
                    allowed_slides = ['LEFT', 'RIGHT']
                    
                for slide_dir in allowed_slides:
                    if slide_dir == 'LEFT':
                        # Try slide Left: (r+1, c-1) if (r, c-1) is empty
                        down_left = (r + 1, c - 1)
                        side_left = (r, c - 1)
                        if (ValidationEngine._is_traversable(state, down_left[0], down_left[1], ignore_coins=True) and 
                            ValidationEngine._is_traversable(state, side_left[0], side_left[1], ignore_coins=True)):
                            if down_left not in visited:
                                visited.add(down_left)
                                queue.append(down_left)
                                
                    elif slide_dir == 'RIGHT':
                        # Try slide Right
                        down_right = (r + 1, c + 1)
                        side_right = (r, c + 1)
                        if (ValidationEngine._is_traversable(state, down_right[0], down_right[1], ignore_coins=True) and 
                            ValidationEngine._is_traversable(state, side_right[0], side_right[1], ignore_coins=True)):
                            if down_right not in visited:
                                visited.add(down_right)
                                queue.append(down_right)

        return False

    @staticmethod
    def _is_traversable(state: GridState, r: int, c: int, ignore_coins: bool = False) -> bool:
        """Check if a cell can be traversed (is valid and not blocked)."""
        if not state.is_valid_pos(r, c):
            return False
            
        entity = state.get_entity_at(r, c)
        if entity is None:
            return True
        
        if ignore_coins and entity.type == EntityType.COIN:
            return True
            
        # Piggybank is solid unless it's the target (handled in loop)
        # Obstacles/Fixed are solid
        return False

    @staticmethod
    def find_solution(initial_state: GridState, max_moves: int = 20) -> Optional[List[str]]:
        """
        Attempt to find a solution using the BFS Solver.
        Returns list of move descriptions if found, else None.
        """
        found, steps, moves = TetracoinSolver.solve_bfs(initial_state, max_depth=max_moves)
        
        if found:
            return [str(m) for m in moves]
        return None
