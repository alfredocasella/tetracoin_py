#!/usr/bin/env python3
import sys
import os
import argparse
import json
import logging
import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tetracoin.level_generator import TetracoinLevelGenerator
from src.tetracoin.difficulty import TetracoinDifficultyAnalyzer
from src.tetracoin.campaign import TetracoinCampaignProgressionGenerator
from src.tetracoin.visualization import TetracoinVisualizer

def main():
    parser = argparse.ArgumentParser(description="Generate a Tetracoin Campaign")
    parser.add_argument("--levels", type=int, default=15, help="Number of levels in campaign")
    parser.add_argument("--tutorial", type=int, default=3, help="Number of tutorial levels")
    parser.add_argument("--boss-interval", type=int, default=5, help="Interval for boss levels")
    parser.add_argument("--output", type=str, default="campaign.json", help="Output JSON file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--viz", action="store_true", help="Print visualization of levels")

    args = parser.parse_args()
    
    # Logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    logger = logging.getLogger("CampaignCLI")
    logger.info(f"Starting Campaign Generation: {args.levels} levels")
    
    # Initialize Components
    lvl_gen = TetracoinLevelGenerator(enable_detailed_logging=args.debug)
    diff_analyzer = TetracoinDifficultyAnalyzer()
    
    campaign_gen = TetracoinCampaignProgressionGenerator(
        level_generator=lvl_gen,
        difficulty_analyzer=diff_analyzer,
        boss_level_interval=args.boss_interval,
        logger=logger
    )
    
    # Generate
    try:
        campaign = campaign_gen.generate_campaign(
            num_levels=args.levels,
            tutorial_levels=args.tutorial
        )
    except Exception as e:
        logger.error(f"Campaign Generation failed: {e}")
        sys.exit(1)
        
    # Process Output
    output_data = {
        "campaign_id": f"CAMP_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "generated_at": str(datetime.datetime.now()),
        "levels": []
    }
    
    print("\n--- Campaign Summary ---")
    for lvl in campaign:
        meta = lvl.level_data.metadata
        
        level_info = {
            "id": lvl.level_id,
            "world": lvl.world_index,
            "difficulty": lvl.difficulty_score,
            "is_boss": lvl.is_boss,
            "is_tutorial": lvl.is_tutorial,
            "grid_size": f"{lvl.level_data.grid.cols}x{lvl.level_data.grid.rows}",
            "coins": meta.num_coins,
            "obstacles": meta.num_obstacles,
            "generation_time": f"{meta.generation_time_seconds:.2f}s"
        }
        
        # Convert Grid for serialization if needed (simple dict)
        # Using existing helper
        level_info['grid_config'] = lvl_gen.grid_generator.to_config_dict(lvl.level_data.grid)
        
        output_data["levels"].append(level_info)
        
        # Print Summary
        type_str = "TUTORIAL" if lvl.is_tutorial else ("BOSS" if lvl.is_boss else "NORMAL")
        print(f"[{lvl.level_id}] W{lvl.world_index} | {type_str:8} | Diff: {lvl.difficulty_score:.1f} | Coins: {meta.num_coins}")
        
        if args.viz:
             print(TetracoinVisualizer.render_static(lvl.level_data.grid))
             print("")

    # Save to File
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)
        
    logger.info(f"Campaign saved to {args.output}")

if __name__ == "__main__":
    main()
