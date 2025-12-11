"""
Tetracoin Difficulty Analyzer.
Unified difficulty engine for the entire project.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple, Any, Dict, Set

from src.tetracoin.spec import GridState, EntityType
# We treat imports inside methods to avoid circular deps if needed, but typings need them
# Using string forward refs for Grid and Move

class DifficultyTier(Enum):
    EASY    = auto()
    MEDIUM  = auto()
    HARD    = auto()
    EXPERT  = auto()

@dataclass(frozen=True)
class DifficultyMetrics:
    """Raw, *un-scaled* values measured on a level/solution pair."""
    collection      : int   # number of mandatory coin pickups
    routing         : int   # accumulated decision complexity (branching factor sum)
    moves           : int   # solution path length
    deception       : int   # unused movable entities (distractors)

@dataclass(frozen=True)
class DifficultyReport:
    """Human-readable + machine-friendly difficulty output."""
    metrics     : DifficultyMetrics
    score       : float            # 0–100 composite difficulty score
    tier        : DifficultyTier   # EASY | MEDIUM | HARD | EXPERT
    breakdown   : Dict[str, float] # normalised contributions per metric


# --------------------------------------------------------------------------- #
#  Core analyser
# --------------------------------------------------------------------------- #
class TetracoinDifficultyAnalyzer:
    """
    Unified difficulty engine for the entire project.
    Call            >>> report = TetracoinDifficultyAnalyzer.analyze(grid, path)
    """

    # === tuning knobs ===
    _WEIGHTS = dict(collection=0.25, routing=0.30, moves=0.25, deception=0.20)

    # hard caps used for normalisation
    _MAX_EXPECTED = dict(collection=20, routing=50, moves=25, deception=10)

    # breakpoints
    _THRESHOLDS = [
        ( 0, 25, DifficultyTier.EASY   ),
        (25, 50, DifficultyTier.MEDIUM ),
        (50, 75, DifficultyTier.HARD   ),
        (75,100, DifficultyTier.EXPERT ),
    ]

    # === public API =======================================================
    @classmethod
    def analyze(cls, grid: GridState, solution_path: List['Move']) -> DifficultyReport:
        """
        Parameters
        ----------
        grid : the immutable level object.
        solution_path : ordered list of moves that solves `grid`.
        """
        raw = cls._measure(grid, solution_path)
        breakdown, score = cls._normalise_and_score(raw)
        tier = cls._tier_for(score)
        return DifficultyReport(metrics=raw, score=score, tier=tier, breakdown=breakdown)

    # === private helpers ===================================================
    @staticmethod
    def _measure(grid: GridState, path: List['Move']) -> DifficultyMetrics:
        """Extract *raw* (un-scaled) difficulty signals from grid + path."""
        # ---- Collection complexity ---------------------------------------
        coins = [e for e in grid.entities if e.type == EntityType.COIN]
        total_required_coins = len(coins)

        # ---- Routing complexity ------------------------------------------
        # In a generic maze, this is spatial branching. 
        # In Tetracoin, it's state-space branching. 
        # We can approximate "Routing/Decision" complexity by checking how many 
        # valid moves exist at each step.
        # But `grid` is the initial state. We'd need to simulate the solution to know exact branching at each step.
        # Simulating full physics here might be expensive.
        # Approximation: "Routing" = Total Movable Entities * Path Length?
        # Or just: How many blocks *could* be moved vs how many *must* be moved.
        # Let's use a simpler heuristic for now to match the prompt's speed expectation:
        # Count movable entities interacting with the "flow columns".
        # Better: Just count distinct movable entities available.
        
        movable_types = (EntityType.OBSTACLE, EntityType.DEFLECTOR, EntityType.SUPPORT)
        movable_count = len([e for e in grid.entities if e.type in movable_types])
        
        # Decision nodes heuristic:
        # If I have N movable blocks, and solution length is L.
        # At each step I theoretically choose between N blocks (and 4 dirs).
        # Complexity ~ L * N.
        # We'll normalize this.
        routing_nodes = len(path) * movable_count

        # ---- Move complexity ---------------------------------------------
        move_count = len(path)

        # ---- Deception complexity ----------------------------------------
        # Entities that exist but are NEVER moved in the solution.
        moved_ids = set(m.entity_id for m in path)
        all_movable = [e for e in grid.entities if e.type in movable_types]
        deception = 0
        for e in all_movable:
            if e.id not in moved_ids:
                deception += 1

        return DifficultyMetrics(
            collection=total_required_coins,
            routing=routing_nodes // 4, # Scale down a bit? Or adjust Max Expected
            moves=move_count,
            deception=deception,
        )

    @classmethod
    def _normalise_and_score(cls, metrics: DifficultyMetrics) -> Tuple[Dict[str, float], float]:
        """Scale each metric to 0-100 and weighted-sum them."""
        b = {}  # per-metric 0-100 contributions
        for key, value in metrics.__dict__.items():
            cap = cls._MAX_EXPECTED.get(key, 100)
            b[key] = min(value / cap, 1.0) * 100

        score = sum(b[k] * cls._WEIGHTS.get(k, 0) for k in b)
        return b, score

    @classmethod
    def _tier_for(cls, score: float) -> DifficultyTier:
        for low, high, tier in cls._THRESHOLDS:
            if low <= score < high:
                return tier
        return DifficultyTier.EXPERT   # fallback (≥ 100)

    # === debugging aid =====================================================
    @staticmethod
    def pretty_print(report: DifficultyReport) -> str:
        m = report.metrics
        head = (
            f"Difficulty: {report.tier.name}  "
            f"(score = {report.score:.1f}/100)\n"
            "---------------------------------------"
        )
        body = (
            f"Collection : {m.collection:3d}  →  {report.breakdown['collection']:6.2f}\n"
            f"Routing    : {m.routing:3d}  →  {report.breakdown['routing']:6.2f}\n"
            f"Moves      : {m.moves:3d}  →  {report.breakdown['moves']:6.2f}\n"
            f"Deception  : {m.deception:3d}  →  {report.breakdown['deception']:6.2f}"
        )
        return f"{head}\n{body}"
