#!/usr/bin/env python3
import sys
import os
import argparse
import json
import logging
import datetime
from typing import List, Dict

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tetracoin.level_generator import TetracoinLevelGenerator
from src.tetracoin.level_generator_spec import TetracoinGenerationConfig, DifficultyLevel, TetracoinLevel
from src.tetracoin.config_validator import TetracoinConfigValidator
from src.tetracoin.solver import TetracoinSolver

def main():
    parser = argparse.ArgumentParser(description="Generate Tetracoin Levels V2")
    parser.add_argument("--count", type=int, default=10, help="Number of levels to generate")
    parser.add_argument("--out", type=str, required=True, help="Output directory")
    parser.add_argument("--curve", type=str, default="EASY,MEDIUM", help="Difficulty curve (comma separated)")

    args = parser.parse_args()
    
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger("TetracoinLevelGenerator").setLevel(logging.DEBUG)
    logging.getLogger("TetracoinSolver").setLevel(logging.DEBUG)
    logger = logging.getLogger("LevelGen")
    
    # 1. Setup
    out_dir = args.out
    os.makedirs(out_dir, exist_ok=True)
    
    curve = [DifficultyLevel[d.upper()] for d in args.curve.split(",")]
    # Cycle curve if count > len(curve)
    
    lvl_gen = TetracoinLevelGenerator(enable_detailed_logging=True, enable_auto_adjustment=False)
    validator = TetracoinConfigValidator()
    solver = TetracoinSolver()
    
    results = []
    
    for i in range(args.count):
        difficulty = curve[i % len(curve)]
        level_index = i + 1
        level_id = f"level_{level_index:03d}"
        
        logger.info(f"Generating {level_id} (Diff: {difficulty.name})...")
        
        # Generator handles built-in validation, but we do extra checks per prompt
        result = lvl_gen.generate(
            level_id=level_id,
            difficulty_target=difficulty,
            force_solvable=True
        )
        
        if isinstance(result, tuple):
            level = result[0]
        else:
            level = result
        
        # 2. Extra Validation
        val_res = validator.validate(lvl_gen.grid_generator.to_config_dict(level.grid))
        val_status = "OK" if val_res.is_valid else "FAIL"
        
        # 3. Solvability Check
        found, steps, moves = solver.solve_bfs(level.grid)
        solution = moves if found else None
        sol_len = steps if found else 0
        sol_status = "OK" if solution else "FAIL"
        
        # GDD: target_moves? Generator doesn't explicitly output target moves yet, 
        # usually derived from solution length.
        target_moves = int(sol_len * 1.2) # Heuristic
        
        # 4. Save
        json_path = os.path.join(out_dir, f"{level_id}.json")
        meta_path = os.path.join(out_dir, f"{level_id}.meta")
        
        # Save Level JSON (using to_level_dict equivalent or internal representation)
        # We need a format compatible with Game loader.
        # src.tetracoin.spec level dict structure.
        level_dict = {
            "id": level.id,
            "grid": {
                "rows": level.grid.rows,
                "cols": level.grid.cols
            },
            "entities": [e.to_dict() for e in level.grid.entities],
            "time_limit": 180, # Default
            # V2 Spec
        }
        
        with open(json_path, 'w') as f:
            json.dump(level_dict, f, indent=2)
            
        # Save Metadata
        meta_dict = {
            "seed": "UNKNOWN", # Generator should expose seed if possible, checking level.metadata
            "difficulty": difficulty.name,
            "solution_length": sol_len,
            "target_moves": target_moves,
            "generation_stats": level.metadata.__dict__.copy()
        }
        meta_dict['generation_stats']['timestamp'] = meta_dict['generation_stats']['timestamp'].isoformat()
        
        with open(meta_path, 'w') as f:
            json.dump(meta_dict, f, indent=2)
            
        results.append({
            "level": level_id,
            "json": json_path,
            "seed": meta_dict['generation_stats'].get('seed', 'N/A'),
            "sol_len": sol_len,
            "target": target_moves,
            "sol_status": sol_status,
            "val_status": val_status
        })
        
        logger.info(f"Saved {level_id}. Sol: {sol_status} ({sol_len} moves). Val: {val_status}")

    # Write summary for report
    with open(os.path.join(out_dir, "solver_results.json"), 'w') as f:
        json.dump(results, f, indent=2)
        
    print("Generation Batch Complete.")

if __name__ == "__main__":
    main()
