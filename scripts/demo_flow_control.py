import sys
import os
import random

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tetracoin.generator import TetracoinGridGenerator
from src.tetracoin.flow_control import FlowControlObstacleAdder

def main():
    print("=== Tetracoin Flow Control Demo ===\n")
    
    difficulties = ["easy", "medium", "hard"]
    
    for diff in difficulties:
        print(f"--- Generating {diff.upper()} Level ---")
        difficulty_int = 1 if diff == "easy" else (5 if diff == "medium" else 8)
        
        gen = TetracoinGridGenerator(
            difficulty=difficulty_int,
            grid_width=8,
            grid_height=10,
            num_coins=6,
            num_piggybanks=2,
            seed=random.randint(0, 10000)
        )
        
        grid = gen.generate(max_attempts=100)
        
        if grid:
            # We can use the adder helper to get ASCII even if adder ran inside generator
            # (The method is stateless regarding the adder instance, takes grid as arg)
            adder = FlowControlObstacleAdder() 
            print(adder.get_ascii_grid(grid))
            
            # Print stats
            obs_count = adder._count_obstacles(grid)
            print(f"\nTotal Obstacles/Flow Items: {obs_count}")
        else:
            print("Failed to generate level.")
        print("\n")

if __name__ == "__main__":
    main()
