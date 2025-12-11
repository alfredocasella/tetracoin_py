from typing import List, Optional, Any, Dict
from dataclasses import dataclass, field
import random
import logging

from src.tetracoin.level_generator import TetracoinLevelGenerator
from src.tetracoin.level_generator_spec import TetracoinGenerationConfig, DifficultyLevel, TetracoinLevel
from src.tetracoin.difficulty import TetracoinDifficultyAnalyzer
from src.tetracoin.spec import GridState

@dataclass
class CampaignLevel:
    """Rappresentazione di un livello all'interno della struttura della campagna."""
    level_id: str
    level_data: TetracoinLevel
    difficulty_score: float
    world_index: int
    is_boss: bool
    is_tutorial: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

class TetracoinCampaignProgressionGenerator:
    """
    Generatore di progressione per la campagna Tetracoin.
    Gestisce la curva di difficoltà, i mondi, i tutorial e i boss levels.
    """
    
    def __init__(
        self,
        level_generator: TetracoinLevelGenerator,
        difficulty_analyzer: TetracoinDifficultyAnalyzer,
        boss_level_interval: int = 10,
        logger: Optional[logging.Logger] = None
    ):
        self.level_generator = level_generator
        self.difficulty_analyzer = difficulty_analyzer
        self.boss_level_interval = boss_level_interval
        self.logger = logger or logging.getLogger("CampaignGen")

    def generate_campaign(self, num_levels: int, tutorial_levels: int = 3) -> List[CampaignLevel]:
        """
        Genera una campagna completa di num_levels.
        
        Struttura:
        - Primi 'tutorial_levels' livelli: Tutorial (Difficoltà molto bassa)
        - Resto: Progressione lineare di difficoltà
        - Ogni 'boss_level_interval': Boss Level (Picco di difficoltà)
        """
        if num_levels <= 0:
            return []
            
        campaign = []
        current_world = 1
        
        # 1. Tutorial Levels
        tutorials_to_gen = min(num_levels, tutorial_levels)
        for i in range(tutorials_to_gen):
            self.logger.info(f"Generating Tutorial Level {i+1}")
            
            # Configurazione Tutorial: Molto facile, pochi elementi
            tut_config = TetracoinGenerationConfig.from_difficulty(DifficultyLevel.EASY)
            tut_config.grid_height = 6 # Piccolo
            tut_config.grid_width = 5
            tut_config.num_coins = 2 + i # Incrementale
            tut_config.obstacle_density = 0.05 * i # Pochissimi ostacoli
            
            # Genera usando config custom
            level = self.level_generator.generate(
                level_id=f"TUT_{i+1:02d}",
                custom_config=tut_config.__dict__, # Hacky but works if dataclass dict matches
                force_solvable=True,
                return_metadata=False
            )
            
            # Analyze real difficulty
            # Assuming level.solution_hint provides moves
            # But we need grid to pass to analyze... level.grid is GridState
            # And analyze takes (grid, solution). Solution is list of moves.
            # level.solution_hint is the list of moves.
            diff_report = self.difficulty_analyzer.analyze(level.grid, level.solution_hint)
            
            campaign.append(CampaignLevel(
                level_id=level.id,
                level_data=level,
                difficulty_score=diff_report.score,
                world_index=0, # World 0 for tutorial
                is_boss=False,
                is_tutorial=True,
                metadata={"tutorial_step": i+1}
            ))
            
        # 2. Main Campaign Levels
        remaining_levels = num_levels - tutorials_to_gen
        start_index = tutorials_to_gen
        
        if remaining_levels <= 0:
            return campaign
            
        # Calcolo curva difficoltà base
        # Range difficoltà target: da 15 (Easy-Medium) a 90 (Expert)
        min_diff = 15.0
        max_diff = 90.0
        
        for i in range(remaining_levels):
            abs_index = start_index + i + 1 # 1-based index total
            rel_index = i # 0-based index in main campaign
            
            is_boss = (abs_index % self.boss_level_interval == 0)
            
            # Target Difficulty calculation
            # Lineare interpolazione
            progress = rel_index / max(1, remaining_levels - 1)
            target_score = min_diff + (max_diff - min_diff) * progress
            
            if is_boss:
                target_score = min(100.0, target_score * 1.2 + 10) # 20% boost + 10 flat
                self.logger.info(f"Generating BOSS Level {abs_index} (Target: {target_score:.1f})")
            else:
                self.logger.info(f"Generating Campaign Level {abs_index} (Target: {target_score:.1f})")
            
            # Determine World (every boss interval constitutes a world usually, or every 10)
            current_world = (abs_index - 1) // self.boss_level_interval + 1
            
            # Map target score to Enum/Config
            if target_score < 30:
                base_diff = DifficultyLevel.EASY
            elif target_score < 60:
                base_diff = DifficultyLevel.MEDIUM
            elif target_score < 85:
                base_diff = DifficultyLevel.HARD
            else:
                base_diff = DifficultyLevel.EXPERT
            
            # Config
            config = TetracoinGenerationConfig.from_difficulty(base_diff)
            # Tweaks for Boss
            if is_boss:
                config.grid_height += 2
                config.num_coins += 3
                config.obstacle_density += 0.1
                config.require_optimal_solution = True # Bosses should be cleaner? or harder?
                
            # Generate
            # Pass target difficulty for auto-adjuster!
            level = self.level_generator.generate(
                level_id=f"LVL_{abs_index:03d}",
                difficulty_target=base_diff, # Coarse target
                # We could use custom_config to pass specific params if needed
                force_solvable=True,
                return_metadata=False
            )
            
            # Re-verify logic: LevelGenerator already auto-adjusts if enabled.
            # But our linear interpolation target_score logic is fine-grained (0-100).
            # LevelGenerator takes Enum.
            # To respect the fine-grained curve better, we might want to manually auto-adjust here?
            # Or trust the generator roughly aligns with the Tier.
            # For this implementation, we trust the generator's Tier targeting and AutoAdjuster internal logic.
            
            diff_report = self.difficulty_analyzer.analyze(level.grid, level.solution_hint)
            
            campaign.append(CampaignLevel(
                level_id=level.id,
                level_data=level,
                difficulty_score=diff_report.score,
                world_index=current_world,
                is_boss=is_boss,
                is_tutorial=False
            ))
            
        return campaign
