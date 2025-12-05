import logging
import random
import uuid
import time
import copy
from typing import Optional, Dict, Any, Union, Tuple, List, Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

from src.tetracoin.level_generator_spec import (
    TetracoinGenerationConfig,
    GenerationStats,
    LevelMetadata,
    TetracoinLevel,
    DifficultyLevel,
    GenerationFailedException,
    InvalidConfigurationException
)
from src.tetracoin.generator import TetracoinGridGenerator
from src.tetracoin.coin_placer import CoinPlacer
from src.tetracoin.flow_control import FlowControlObstacleAdder
from src.tetracoin.solver import TetracoinSolver
from src.tetracoin.difficulty import TetracoinDifficultyAnalyzer
from src.tetracoin.auto_adjuster import TetracoinAutoAdjuster
from src.tetracoin.config_validator import TetracoinConfigValidator, ValidationResult
from src.tetracoin.spec import GridState

class TetracoinLevelGenerator:
    """
    Generatore end-to-end per livelli Tetracoin.
    Orchestra tutti i componenti per produrre livelli validi, bilanciati e testati.
    """
    
    def __init__(
        self,
        config: Optional[TetracoinGenerationConfig] = None,
        grid_generator: Optional[TetracoinGridGenerator] = None,
        coin_placer: Optional[CoinPlacer] = None,
        obstacle_adder: Optional[FlowControlObstacleAdder] = None,
        solver: Optional[TetracoinSolver] = None,
        difficulty_analyzer: Optional[TetracoinDifficultyAnalyzer] = None,
        auto_adjuster: Optional[TetracoinAutoAdjuster] = None,
        config_validator: Optional[TetracoinConfigValidator] = None,
        logger: Optional[logging.Logger] = None,
        enable_auto_adjustment: bool = True,
        max_generation_attempts: int = 10,
        enable_detailed_logging: bool = False
    ) -> None:
        
        # Setup Config
        self.config = config or TetracoinGenerationConfig.default()
        
        # Setup Logger
        self.logger = logger or logging.getLogger("TetracoinLevelGenerator")
        if enable_detailed_logging:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
            
        # Init Components (create defaults if not provided)
        # We need to initialize basic components with current config if creating defaults
        self.grid_generator = grid_generator or TetracoinGridGenerator(
            difficulty=1, # Placeholder, will be overriden by config in pipeline if needed
            grid_width=self.config.grid_width,
            grid_height=self.config.grid_height,
            num_coins=self.config.num_coins,
            num_piggybanks=self.config.num_piggybanks
        )
        self.coin_placer = coin_placer or CoinPlacer(rng=random)
        self.obstacle_adder = obstacle_adder or FlowControlObstacleAdder(rng=random)
        self.solver = solver or TetracoinSolver()
        self.difficulty_analyzer = difficulty_analyzer or TetracoinDifficultyAnalyzer()
        self.auto_adjuster = auto_adjuster or TetracoinAutoAdjuster()
        self.config_validator = config_validator or TetracoinConfigValidator()
        
        self.enable_auto_adjustment = enable_auto_adjustment
        self.max_generation_attempts = max_generation_attempts
        self.stats = GenerationStats()
        
        # Initial Validation
        # Validiamo la config di base al boot
        # (Opzionale: potremmo saltare se vogliamo permettere config invalidi fino al generate)
    
    def generate(
        self,
        level_id: Optional[str] = None,
        difficulty_target: Optional[DifficultyLevel] = None,
        seed: Optional[int] = None,
        custom_config: Optional[Dict[str, Any]] = None,
        force_solvable: bool = True,
        return_metadata: bool = True
    ) -> Union[TetracoinLevel, Tuple[TetracoinLevel, LevelMetadata]]:
        """
        Genera un singolo livello Tetracoin completo.
        """
        start_time = time.time()
        
        # 1. Setup
        if seed is not None:
            random.seed(seed)
        
        actual_level_id = level_id or uuid.uuid4().hex[:12]
        
        # Mixin Config
        current_config = copy.deepcopy(self.config)
        if difficulty_target:
            current_config = TetracoinGenerationConfig.from_difficulty(difficulty_target)
            
        if custom_config:
            # Simple override (deep merge would be better but keeping it simple)
            for k, v in custom_config.items():
                if hasattr(current_config, k):
                    setattr(current_config, k, v)
        
        # Sync GridGenerator with current config
        self.grid_generator.width = current_config.grid_width
        self.grid_generator.height = current_config.grid_height
        self.grid_generator.num_piggybanks = current_config.num_piggybanks
        self.grid_generator.num_coins = current_config.num_coins
        self.grid_generator.difficulty = 5 # Default context
        if difficulty_target:
             # Map enum to 1-10 int roughly
             mapping = {
                 DifficultyLevel.EASY: 2,
                 DifficultyLevel.MEDIUM: 5,
                 DifficultyLevel.HARD: 8,
                 DifficultyLevel.EXPERT: 10
             }
             self.grid_generator.difficulty = mapping.get(difficulty_target, 5)

        attempts_made = 0
        self.stats.total_attempts += 1 # Count the high-level request as one attempt? 
        # Or count inner attempts? Let's trace inner logic.
        
        for attempt in range(1, self.max_generation_attempts + 1):
            attempts_made = attempt
            try:
                self.logger.debug(f"Generation attempt {attempt}/{self.max_generation_attempts} for Level {actual_level_id}")
                
                # 2.1 Genera Struttura
                grid = self.grid_generator.generate_structure()
                if not grid:
                    raise GenerationFailedException("Grid structure generation failed")
                
                # 2.2 Position Coins
                # CoinPlacer logic uses 'difficulty' integer usually.
                # using mapping from current config or passed difficulty
                numeric_difficulty = self.grid_generator.difficulty
                
                if not self.coin_placer.place_coins_strategic(grid, current_config.num_coins, numeric_difficulty):
                    self.logger.debug("Coin placement failed")
                    continue
                
                # 2.3 Add Obstacles
                grid = self.obstacle_adder.add_obstacles(grid, numeric_difficulty)
                
                # 2.4 Verify Solvability
                # TetracoinSolver.solve_bfs returns (found, steps, moves)
                # max_depth based on difficulty
                max_depth = 8 + numeric_difficulty * 2
                
                is_solvable, steps, moves = self.solver.solve_bfs(
                    GridState(rows=grid.rows, cols=grid.cols, entities=grid.entities), 
                    max_depth=max_depth
                )
                
                if not is_solvable:
                    self.stats.increment_unsolvable_attempts()
                    if force_solvable:
                        self.logger.debug("Level not solvable, retrying...")
                        continue
                    else:
                        self.logger.warning("Generated unsolvable level (force_solvable=False)")
                
                # 2.5 Analyze Difficulty
                # DifficultyAnalyzer expects GridState and Moves
                # If unsolvable and forced is False, moves is empty list probably.
                difficulty_report = self.difficulty_analyzer.analyze(grid, moves)
                
                # 2.6 Auto-adjustment
                # Only if solvable (otherwise score is invalid usually) and enabled
                if is_solvable and self.enable_auto_adjustment and difficulty_target:
                    # Target score logic:
                    target_score_map = {
                        DifficultyLevel.EASY: 25.0,
                        DifficultyLevel.MEDIUM: 50.0,
                        DifficultyLevel.HARD: 75.0,
                        DifficultyLevel.EXPERT: 90.0
                    }
                    target_score_val = target_score_map.get(difficulty_target, 50.0)
                    
                    # Convert to 0-1 range for adjuster if needed, or check logic
                    # AutoAdjuster takes 0-1 float target.
                    target_0_1 = target_score_val / 100.0
                    
                    # Check tolerance (e.g. +/- 15 points)
                    current_score = difficulty_report.score
                    if abs(current_score - target_score_val) > 15:
                         self.logger.debug(f"Adjusting difficulty: {current_score} -> {target_score_val}")
                         adjust_res = self.auto_adjuster.auto_adjust(grid, target_0_1, max_iterations=current_config.max_adjustment_iterations)
                         if adjust_res.success:
                             grid = adjust_res.grid
                             # Re-solve and Re-analyze
                             is_solvable, steps, moves = self.solver.solve_bfs(
                                GridState(rows=grid.rows, cols=grid.cols, entities=grid.entities), 
                                max_depth=max_depth
                             )
                             difficulty_report = self.difficulty_analyzer.analyze(grid, moves)
                
                # 2.7 Final Validation
                # Validate using config dictionary format
                config_dict = self.grid_generator.to_config_dict(grid)
                validation_res = self.config_validator.validate(config_dict)
                
                if not validation_res.is_valid:
                    self.logger.debug(f"Validation failed: {validation_res.errors}")
                    self.stats.increment_validation_failures()
                    continue
                    
                # 2.8 Success
                elapsed = time.time() - start_time
                self.stats.increment_successful_generations()
                self.stats.add_generation_time(elapsed)
                
                # Prepare Output
                metadata = LevelMetadata(
                    level_id=actual_level_id,
                    generation_attempts=attempts_made,
                    generation_time_seconds=elapsed,
                    difficulty_score=difficulty_report.score,
                    difficulty_tier=difficulty_report.tier.name,
                    solution_length=len(moves),
                    num_coins=len(current_config.num_coins) if isinstance(current_config.num_coins, list) else current_config.num_coins, # Fix: num_coins is int
                    num_obstacles=len(config_dict['obstacles']),
                    grid_dimensions=(current_config.grid_width, current_config.grid_height),
                    seed_used=seed
                )
                # Fix num_coins read
                metadata.num_coins = len([e for e in grid.entities if e.type == 'COIN']) # Better count directly
                
                level = TetracoinLevel(
                    id=actual_level_id,
                    grid=grid,
                    config=current_config,
                    metadata=metadata,
                    solution_hint=moves
                )
                
                self.logger.info(f"Level {actual_level_id} generated in {attempts_made} attempts. Score: {difficulty_report.score}")
                
                return (level, metadata) if return_metadata else level
                
            except Exception as e:
                self.logger.error(f"Attempt {attempt} failed: {e}")
                self.stats.increment_exception_count()
                continue
                
        raise GenerationFailedException(f"Failed to generate level after {self.max_generation_attempts} attempts")

    def generate_batch(
        self,
        num_levels: int,
        difficulty_distribution: Optional[Dict[DifficultyLevel, float]] = None,
        base_level_id_prefix: Optional[str] = None,
        seed_start: Optional[int] = None,
        parallel: bool = False,
        num_workers: Optional[int] = None,
        return_metadata: bool = True
    ) -> Union[List[TetracoinLevel], List[Tuple[TetracoinLevel, LevelMetadata]]]:
        """Genera un batch di livelli."""
        if num_levels <= 0:
            raise ValueError("num_levels must be positive")
            
        # Distribution Logic
        dist = difficulty_distribution or {DifficultyLevel.MEDIUM: 1.0}
        
        # Calculate targets
        targets = []
        current_count = 0
        keys = list(dist.keys())
        
        for k in keys[:-1]:
            count = int(num_levels * dist[k])
            targets.extend([k] * count)
            current_count += count
        
        # Fill rest with last key to ensure sum match
        targets.extend([keys[-1]] * (num_levels - current_count))
        random.shuffle(targets)
        
        levels = []
        
        if parallel:
            # Parallel Execution
            num_workers = num_workers or os.cpu_count() or 1
            
            # Prepare Tasks
            tasks = []
            for i in range(num_levels):
                tasks.append({
                    'level_id': f"{base_level_id_prefix or 'lvl'}_{i:03d}",
                    'difficulty_target': targets[i],
                    'seed': seed_start + i if seed_start is not None else None,
                    'return_metadata': return_metadata,
                    'config': self.config # Pass config copy
                })
            
            final_results = []
            
            with ProcessPoolExecutor(max_workers=num_workers) as executor:
                futures = {executor.submit(self._generate_worker, t): i for i, t in enumerate(tasks)}
                
                for future in as_completed(futures):
                    try:
                        res = future.result()
                        if res:
                            final_results.append(res)
                            self.stats.increment_successful_generations() # Approx update (race condition on simple int, but stats not shared back from process)
                    except Exception as e:
                        self.logger.error(f"Worker failed: {e}")
            
            # Sort by ID if possible or just return
            return final_results

        # Sequential Execution
        levels = []
        for i in range(num_levels):
            lid = f"{base_level_id_prefix or 'lvl'}_{i:03d}"
            sd = seed_start + i if seed_start is not None else None
            
            try:
                res = self.generate(
                    level_id=lid,
                    difficulty_target=targets[i],
                    seed=sd,
                    return_metadata=return_metadata
                )
                levels.append(res)
            except GenerationFailedException:
                self.logger.error(f"Failed to generate level {i} in batch")
                continue
                
        return levels

    @staticmethod
    def _generate_worker(task: Dict[str, Any]) -> Any:
        # Re-hydrate generator
        # Note: This is an expensive per-task setup. Ideally worker initializes once.
        # But for simplicity:
        config = task.get('config')
        gen = TetracoinLevelGenerator(config=config)
        
        try:
            return gen.generate(
                level_id=task['level_id'],
                difficulty_target=task['difficulty_target'],
                seed=task['seed'],
                return_metadata=task['return_metadata']
            )
        except:
            return None

    # Helper Factories
    @classmethod
    def default(cls) -> 'TetracoinLevelGenerator':
        return cls()
        
    @classmethod
    def from_preset(cls, preset_name: str) -> 'TetracoinLevelGenerator':
        if preset_name == "easy_casual":
            cfg = TetracoinGenerationConfig.from_difficulty(DifficultyLevel.EASY)
            return cls(config=cfg)
        # Add others...
        return cls.default()
