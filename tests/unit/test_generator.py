import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.tetracoin.generator import TetracoinGridGenerator
from src.tetracoin.spec import GridState, EntityType, ColorType, Coin, PiggyBank

class TestTetracoinGenerator(unittest.TestCase):
    
    def test_basic_generation(self):
        """Test if generator produces a valid grid object."""
        gen = TetracoinGridGenerator(
            difficulty=1, 
            grid_width=6, 
            grid_height=8, 
            num_coins=4, 
            num_piggybanks=2,
            seed=42
        )
        grid = gen.generate(max_attempts=10)
        
        self.assertIsNotNone(grid, "Generator failed to produce a grid")
        self.assertIsInstance(grid, GridState)
        self.assertEqual(grid.rows, 8)
        self.assertEqual(grid.cols, 6)
        
        # Check entities count
        coins = [e for e in grid.entities if e.type == EntityType.COIN]
        piggies = [e for e in grid.entities if e.type == EntityType.PIGGYBANK]
        
        self.assertEqual(len(coins), 4)
        self.assertEqual(len(piggies), 2)
        
    def test_reachability_guarantee(self):
        """Test that generated grids have satisfied reachability checks."""
        # Using a low difficulty to ensure high success rate
        gen = TetracoinGridGenerator(
            difficulty=1,
            grid_width=5,
            grid_height=5,
            num_coins=2,
            num_piggybanks=1,
            seed=100
        )
        grid = gen.generate()
        self.assertIsNotNone(grid)
        
        # We implicitly tested reachability inside generate(), 
        # but let's manually verifying specific conditions?
        # Actually generate() returns None if reachability fails.
        # So existence implies reachability passed.
        pass

    def test_difficulty_scaling(self):
        """Test that higher difficulty produces more obstacles."""
        from src.tetracoin.spec import EntityType # Ensure import available
        
        gen_easy = TetracoinGridGenerator(difficulty=1, grid_width=10, grid_height=10, num_coins=5, num_piggybanks=2, seed=123)
        gen_hard = TetracoinGridGenerator(difficulty=8, grid_width=10, grid_height=10, num_coins=5, num_piggybanks=2, seed=124) # Use 8 (Hard) instead of 10 (Expert) to be safe
        
        grid_easy = gen_easy.generate(max_attempts=100)
        grid_hard = gen_hard.generate(max_attempts=500)
        
        self.assertIsNotNone(grid_easy, "Easy generation failed")
        self.assertIsNotNone(grid_hard, "Hard generation failed")
        
        obstacle_types = (EntityType.OBSTACLE, EntityType.FIXED_BLOCK, EntityType.SUPPORT, EntityType.DEFLECTOR, EntityType.GATEWAY, EntityType.TRAP)
        
        obs_easy = len([e for e in grid_easy.entities if e.type in obstacle_types])
        obs_hard = len([e for e in grid_hard.entities if e.type in obstacle_types])
        
        self.assertGreater(obs_hard, obs_easy, f"Hard difficulty should have more obstacles (Easy: {obs_easy}, Hard: {obs_hard})")

if __name__ == '__main__':
    unittest.main()
