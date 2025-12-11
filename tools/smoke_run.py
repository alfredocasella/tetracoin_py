#!/usr/bin/env python3
import sys
import os
import argparse
import time
import pygame
from pathlib import Path

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import Game
from core.settings import *
from core.game import Game
from src.tetracoin.spec import GridState

def main():
    parser = argparse.ArgumentParser(description="Tetracoin Smoke Test Runner")
    parser.add_argument("--levels", type=str, required=True, help="Directory containing levels")
    parser.add_argument("--headless", action="store_true", help="Run without window (dummy video driver)")
    parser.add_argument("--limit", type=int, default=10, help="Max levels to test")
    
    args = parser.parse_args()
    
    if args.headless:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        
    print(f"--- Smoke Test Starting: {args.levels} ---")
    
    # Init Game Wrapper
    # Initialize Pygame explicitly if Game() doesn't do it cleanly for headless
    pygame.init()
    
    # We need to hack Game to load specific file paths instead of internal level loader indices
    # Or we can patch LevelLoader.
    
    game = Game()
    
    level_files = sorted(Path(args.levels).glob("*.json"))
    if not level_files:
        print("No level files found!")
        sys.exit(1)
        
    level_files = level_files[:args.limit]
    
    stats = {
        "passed": 0,
        "failed": 0,
        "avg_load_time": 0.0,
        "errors": []
    }
    
    total_load_time = 0.0
    
    for lvl_path in level_files:
        lvl_id = lvl_path.stem
        print(f"Testing {lvl_id}...", end="", flush=True)
        
        try:
            start_t = time.time()
            
            # Load JSON manually
            import json
            with open(lvl_path, 'r') as f:
                level_data = json.load(f)
                
            # Inject into game
            game.level_data = level_data
            game.use_json_levels = True # Force flag
            
            # Trigger logic that Game.load_level does
            # Ensure mode is PHYSICS
            if 'entities' in level_data:
                game.mode = "PHYSICS"
                game._init_physics_level()
            else:
                 raise ValueError("Legacy level format not supported in smoke test")
            
            # Simulate a few updates
            game.state = game.STATE_PLAY
            dt = 0.016 # 60 FPS
            for _ in range(10): # 10 frames
                game.update(dt)
                
            load_dur = (time.time() - start_t) * 1000 # ms
            total_load_time += load_dur
            
            print(f" OK ({load_dur:.1f}ms)")
            stats["passed"] += 1
            
        except Exception as e:
            print(f" FAIL: {e}")
            stats["failed"] += 1
            stats["errors"].append(f"{lvl_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            
    stats["avg_load_time"] = total_load_time / max(1, stats["passed"])
    
    print("\n--- Smoke Test Results ---")
    print(f"Passed: {stats['passed']}")
    print(f"Failed: {stats['failed']}")
    print(f"Avg Load Time: {stats['avg_load_time']:.2f} ms")
    
    if stats["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
