from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Callable
from enum import Enum, auto
import datetime
import uuid

# --- Enums ---

class DifficultyLevel(Enum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()
    EXPERT = auto()

# --- Configuration ---

@dataclass
class TerrainConfig:
    """Configurazione per il terreno di base."""
    pass # Placeholder per configurazioni future del terreno

@dataclass
class StructuralObstaclesConfig:
    """Configurazione per ostacoli strutturali (fissi)."""
    pass # Placeholder

@dataclass
class TetracoinGenerationConfig:
    """Configurazione completa per la generazione di un livello."""
    # Settings Base
    grid_width: int = 8
    grid_height: int = 10
    num_coins: int = 5
    num_piggybanks: int = 2
    
    # Components Config
    terrain_config: Optional[TerrainConfig] = None
    structural_obstacles_config: Optional[StructuralObstaclesConfig] = None
    
    # Strategies
    coin_placement_strategy: str = "balanced"
    coin_constraints: Dict[str, Any] = field(default_factory=dict)
    
    # Obstacles
    flow_obstacles: List[str] = field(default_factory=lambda: ["support", "deflector"])
    obstacle_density: float = 0.2
    obstacle_strategy: str = "strategic"
    
    # Solver / Validation
    solver_timeout: float = 2.0
    require_optimal_solution: bool = False
    
    # Auto Adjustment
    max_adjustment_iterations: int = 20
    
    @classmethod
    def default(cls) -> 'TetracoinGenerationConfig':
        return cls()
        
    @classmethod
    def from_difficulty(cls, difficulty: DifficultyLevel) -> 'TetracoinGenerationConfig':
        """Factory method per creare config basati sulla difficoltà."""
        if difficulty == DifficultyLevel.EASY:
            return cls(grid_width=6, grid_height=8, num_coins=3, num_piggybanks=2, obstacle_density=0.1)
        elif difficulty == DifficultyLevel.MEDIUM:
            return cls(grid_width=8, grid_height=10, num_coins=5, num_piggybanks=2, obstacle_density=0.2)
        elif difficulty == DifficultyLevel.HARD:
            return cls(grid_width=10, grid_height=12, num_coins=8, num_piggybanks=3, obstacle_density=0.3)
        elif difficulty == DifficultyLevel.EXPERT:
            return cls(grid_width=12, grid_height=15, num_coins=12, num_piggybanks=3, obstacle_density=0.4)
        return cls.default()

# --- Metadata & Stats ---

@dataclass
class GenerationStats:
    """Statistiche aggregate di generazione."""
    total_attempts: int = 0
    successful_generations: int = 0
    unsolvable_attempts: int = 0
    validation_failures: int = 0
    exception_count: int = 0
    total_generation_time: float = 0.0
    
    @property
    def average_generation_time(self) -> float:
        if self.successful_generations == 0:
            return 0.0
        return self.total_generation_time / self.successful_generations
        
    @property
    def success_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.successful_generations / self.total_attempts

    def increment_successful_generations(self):
        self.successful_generations += 1
        
    def increment_unsolvable_attempts(self):
        self.unsolvable_attempts += 1
        
    def increment_validation_failures(self):
        self.validation_failures += 1
        
    def increment_exception_count(self):
        self.exception_count += 1
        
    def add_generation_time(self, time: float):
        self.total_generation_time += time

@dataclass
class LevelMetadata:
    """Metadata dettagliati per un livello generato."""
    level_id: str
    generation_attempts: int
    generation_time_seconds: float
    difficulty_score: float
    difficulty_tier: str # E.g. "MEDIUM"
    solution_length: int
    num_coins: int
    num_obstacles: int
    grid_dimensions: Tuple[int, int]
    seed_used: Optional[int]
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

# --- Results ---

@dataclass
class TetracoinLevel:
    """Rappresentazione finale del livello per l'uso esterno (senza dettagli interni non necessari)."""
    id: str
    grid: Any # GridState
    config: TetracoinGenerationConfig
    metadata: LevelMetadata
    solution_hint: Optional[List[Any]] = None # List[Move]

# --- Exceptions ---

class GenerationFailedException(Exception):
    """Sollevata quando la generazione fallisce dopo tutti i tentativi."""
    pass

class InvalidConfigurationException(Exception):
    """Sollevata quando la configurazione fornita è invalida."""
    pass

class SolverTimeoutException(Exception):
    """Sollevata quando il solver va in timeout."""
    pass
