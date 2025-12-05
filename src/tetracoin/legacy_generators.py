import warnings
from typing import Dict, Any

from src.tetracoin.level_generator import TetracoinLevelGenerator
from src.tetracoin.level_generator_spec import DifficultyLevel

def generate_drop_away_level(*args, **kwargs) -> Dict[str, Any]:
    """
    DEPRECATED: Wrapper per compatibilità con Drop Away.
    """
    warnings.warn(
        "generate_drop_away_level è deprecato. Usa TetracoinLevelGenerator.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Use Factory or Default
    generator = TetracoinLevelGenerator.from_preset("easy_casual")
    level, metadata = generator.generate(return_metadata=True)
    
    # Convert to legacy dict format if needed
    # Assuming legacy expected a specific structure, we map basics
    return {
        "id": level.id,
        "grid": generator.grid_generator.to_config_dict(level.grid), # Use helper
        "difficulty": level.metadata.difficulty_score
    }

def generate_coin_drop_level(*args, **kwargs) -> Dict[str, Any]:
    """
    DEPRECATED: Wrapper per compatibilità con Coin Drop.
    """
    warnings.warn(
        "generate_coin_drop_level è deprecato. Usa TetracoinLevelGenerator.",
        DeprecationWarning,
        stacklevel=2
    )
    
    generator = TetracoinLevelGenerator.default()
    level, metadata = generator.generate(return_metadata=True)
    
    return {
        "id": level.id,
        "grid": generator.grid_generator.to_config_dict(level.grid),
        "difficulty": level.metadata.difficulty_score
    }
