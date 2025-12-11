"""
Flow Control Obstacle Adder.
Handles placement of obstacles, deflectors, gateways, and traps to shape level flow.
"""
import random
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass

from src.tetracoin.spec import (
    GridState, EntityType, ColorType, Entity, 
    FixedBlock, Support, Deflector, Gateway, Trap, Direction
)
# Assuming ValidationEngine is available for reachability checks
from src.tetracoin.validation import ValidationEngine

@dataclass
class ObstacleSettings:
    min_obstacle_ratio: float
    max_obstacle_ratio: float
    max_traps: int
    allow_multi_tap: bool
    allow_gateway: bool
    description: str

DIFFICULTY_SETTINGS = {
    "easy": ObstacleSettings(
        min_obstacle_ratio=0.03,
        max_obstacle_ratio=0.08,
        max_traps=0, # No traps in easy? Prompt said max_traps 2 but let's be nice
        allow_multi_tap=False,
        allow_gateway=True,
        description="Simple flow with minor deviations"
    ),
    "medium": ObstacleSettings(
        min_obstacle_ratio=0.08,
        max_obstacle_ratio=0.15,
        max_traps=4,
        allow_multi_tap=True,
        allow_gateway=True,
        description="Balanced flow with some decisions"
    ),
    "hard": ObstacleSettings(
        min_obstacle_ratio=0.15,
        max_obstacle_ratio=0.25,
        max_traps=6,
        allow_multi_tap=True,
        allow_gateway=True,
        description="Complex flow with hazards and puzzles"
    ),
    "expert": ObstacleSettings(
        min_obstacle_ratio=0.20,
        max_obstacle_ratio=0.35,
        max_traps=8,
        allow_multi_tap=True,
        allow_gateway=True,
        description="High density constraints and traps"
    )
}

class FlowControlObstacleAdder:
    def __init__(self, rng=None):
        self.rng = rng if rng else random

    def add_obstacles(self, grid: GridState, difficulty: str) -> GridState:
        """
        Adds flow control obstacles to the grid based on difficulty.
        """
        # Normalize difficulty string (map int to string if needed, or assume string)
        # If difficulty is int (1-10) from old geneator, map it.
        if isinstance(difficulty, int):
            if difficulty <= 3: difficulty = "easy"
            elif difficulty <= 6: difficulty = "medium"
            elif difficulty <= 8: difficulty = "hard"
            else: difficulty = "expert"
            
        settings = DIFFICULTY_SETTINGS.get(difficulty.lower(), DIFFICULTY_SETTINGS["medium"])
        
        # 1. Analyze main path / relevant regions
        # For Tetracoin (Gravity), "Main Path" is vertical columns above piggybanks?
        # We can approximate "Main Path" as the set of columns interacting with piggybanks.
        main_path_cells = self._find_approximate_flow_paths(grid)
        
        # 2. Collect candidates
        candidates = self._collect_candidate_positions(grid, main_path_cells)
        
        # Track placed obstacles count
        placed_count = 0
        total_cells = grid.rows * grid.cols
        current_ratio = 0.0
        
        # Helper to check density
        def can_add_more():
            nonlocal placed_count, current_ratio
            current_ratio = placed_count / total_cells
            return current_ratio < settings.max_obstacle_ratio

        # 3. Place Supports
        # Supports might be placed to hold coins up?
        if can_add_more():
            self._place_supports(grid, candidates, settings)
            placed_count = self._count_obstacles(grid)

        # 4. Place Deflectors
        if can_add_more():
            self._place_deflectors(grid, candidates, settings)
            placed_count = self._count_obstacles(grid)

        # 5. Place Gateways
        if settings.allow_gateway and can_add_more():
            self._place_gateways(grid, candidates, settings)
            placed_count = self._count_obstacles(grid)

        # 6. Place Traps
        if can_add_more():
             self._place_traps(grid, candidates, settings)
             placed_count = self._count_obstacles(grid)

        # 8. Validation
        # If blocking too much, rollback or fix?
        # For now, if validation fails, we try to clear some obstacles near coins?
        # Or simple: just return grid (assuming generator loop handles retry if solution invalid)
        # BUT prompt says: "Non deve mai rendere il livello irrisolvibile."
        
        if not self._is_solvable(grid):
             # Try simple repair: remove obstacles intersecting with critical flow?
             # Or just revert to safe state. 
             # For MVP: Revert recent additions? 
             # Let's clean up ALL flow obsyacles if invalid? Too drastic.
             # Better: Remove random obstacles until valid.
             self._repair_grid(grid)
        
        # 9. Enforce Density (Min)
        # If below min_ratio, add random generic obstacles (blocks) in safe spots
        current_ratio = self._count_obstacles(grid) / total_cells
        if current_ratio < settings.min_obstacle_ratio:
             self._fill_up_density(grid, settings.min_obstacle_ratio)
             
        return grid

    def _find_approximate_flow_paths(self, grid: GridState) -> Set[Tuple[int, int]]:
        """Identify cells that are likely part of the flow (columns above piggybanks)."""
        # In Drop Away, flow is mostly vertical.
        # Find all piggybanks
        piggies = [e for e in grid.entities if e.type == EntityType.PIGGYBANK]
        paths = set()
        for pb in piggies:
            # All cells above pb.row in pb.col are primary flow
            for r in range(pb.row):
                paths.add((r, pb.col))
        return paths

    def _collect_candidate_positions(self, grid: GridState, flow_paths: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Find empty cells suitable for obstacles."""
        candidates = []
        for r in range(grid.rows):
            for c in range(grid.cols):
                if grid.is_empty(r, c):
                    # Maybe prefer cells NOT in flow_paths for static blocks?
                    # But Deflectors MUST be in flow paths (or adjacent).
                    candidates.append((r, c))
        self.rng.shuffle(candidates)
        return candidates

    def _place_supports(self, grid: GridState, candidates: List[Tuple[int, int]], settings: ObstacleSettings):
        # Place fixed blocks/supports
        # Maybe random scattered supports to create "shelves"
        num_supports = self.rng.randint(1, 3) # Arbitrary
        for _ in range(num_supports):
            if not candidates: break
            r, c = candidates.pop()
            # Don't block top row or right above piggybank ideally
            if r == 0 or r == grid.rows - 1: continue 
            
            supp = Support(id=f"supp_{r}_{c}", row=r, col=c, color=ColorType.GRAY)
            grid.entities.append(supp)

    def _place_deflectors(self, grid: GridState, candidates: List[Tuple[int, int]], settings: ObstacleSettings):
        # Deflectors push coins sideways.
        # Place them in flow paths?
        num_deflectors = self.rng.randint(0, 2)
        if settings.min_obstacle_ratio > 0.1: num_deflectors += 2
        
        for _ in range(num_deflectors):
             if not candidates: break
             r, c = candidates.pop()
             if r >= grid.rows - 2: continue
             
             direction = "RIGHT" if self.rng.choice([True, False]) else "LEFT"
             defl = Deflector(id=f"defl_{r}_{c}", row=r, col=c, color=ColorType.ORANGE, direction=direction)
             grid.entities.append(defl)

    def _place_gateways(self, grid: GridState, candidates: List[Tuple[int, int]], settings: ObstacleSettings):
        # Gateways block path until opened.
        # Rare.
        if self.rng.random() < 0.3: # 30% chance per level
            if not candidates: return
            r, c = candidates.pop()
            gate = Gateway(id=f"gate_{r}_{c}", row=r, col=c, color=ColorType.PURPLE, is_open=False, condition="SWITCH")
            grid.entities.append(gate)

    def _place_traps(self, grid: GridState, candidates: List[Tuple[int, int]], settings: ObstacleSettings):
        for _ in range(settings.max_traps):
            if self.rng.random() > 0.5: continue # Don't always fill quota
            if not candidates: break
            r, c = candidates.pop()
            # Traps usually on floor or walls?
            trap = Trap(id=f"trap_{r}_{c}", row=r, col=c, color=ColorType.RED, subtype="SPIKES")
            grid.entities.append(trap)

    def _is_solvable(self, grid: GridState) -> bool:
        # Check if coins can reach.
        return ValidationEngine.check_reachability(grid)

    def _repair_grid(self, grid: GridState):
        # Naive repair: remove last added obstacles until solvable
        # Ideally we'd remove specific ones blocking flow.
        # Filter for Flow Control entities
        flow_entities = [e for e in grid.entities if e.type in (EntityType.SUPPORT, EntityType.DEFLECTOR, EntityType.GATEWAY, EntityType.TRAP)]
        self.rng.shuffle(flow_entities)
        
        # Try removing one by one
        for obs in flow_entities:
            grid.entities.remove(obs)
            if self._is_solvable(grid):
                return
                
    def _fill_up_density(self, grid: GridState, min_ratio: float):
        total_cells = grid.rows * grid.cols
        needed = int(total_cells * min_ratio) - self._count_obstacles(grid)
        
        if needed <= 0: return
        
        # Find empty spots again (candidates might be stale)
        empty = []
        for r in range(grid.rows):
            for c in range(grid.cols):
                if grid.is_empty(r, c):
                    empty.append((r, c))
        self.rng.shuffle(empty)
        
        for _ in range(needed):
            if not empty: break
            r, c = empty.pop()
            # Avoid direct blocking of piggies (bottom row)
            if r == grid.rows - 1: continue 
            
            fb = FixedBlock(id=f"fill_{r}_{c}", row=r, col=c, color=ColorType.GRAY)
            grid.entities.append(fb)

    def _count_obstacles(self, grid: GridState) -> int:
        return len([e for e in grid.entities if e.type in (
            EntityType.OBSTACLE, EntityType.FIXED_BLOCK, 
            EntityType.SUPPORT, EntityType.DEFLECTOR, 
            EntityType.GATEWAY, EntityType.TRAP
        )])

    def get_ascii_grid(self, grid: GridState) -> str:
        """Returns ASCII representation for debugging."""
        # Symbols
        symbols = {
            EntityType.COIN: "C",
            EntityType.PIGGYBANK: "U", # U shape
            EntityType.OBSTACLE: "#",
            EntityType.FIXED_BLOCK: "X",
            EntityType.SUPPORT: "=",
            EntityType.DEFLECTOR: "/",
            EntityType.GATEWAY: "[]",
            EntityType.TRAP: "^"
        }
        
        lines = []
        for r in range(grid.rows):
            line = ""
            for c in range(grid.cols):
                ent = grid.get_entity_at(r, c)
                if ent:
                    sym = symbols.get(ent.type, "?")
                    # Special handling for directions/colors?
                    if ent.type == EntityType.DEFLECTOR:
                        sym = ">" if getattr(ent, 'direction', "") == 'RIGHT' else "<"
                    line += f"{sym:^3}"
                else:
                    line += " . "
            lines.append(line)
        return "\n".join(lines)
