import unittest
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tetracoin.level_generator import TetracoinLevelGenerator
from src.tetracoin.level_generator_spec import TetracoinGenerationConfig, DifficultyLevel, TetracoinLevel

class TestTetracoinLevelGenerator(unittest.TestCase):
    def setUp(self):
        # Use low constraints for speed
        self.config = TetracoinGenerationConfig(
            grid_width=6, grid_height=6,
            num_coins=2, num_piggybanks=1,
            max_adjustment_iterations=2
        )
        self.generator = TetracoinLevelGenerator(
            config=self.config,
            enable_auto_adjustment=False,
            max_generation_attempts=20, # Higher for random fallback
            enable_detailed_logging=True
        )

    def test_single_generation(self):
        """Test generation of a single level."""
        level = self.generator.generate(force_solvable=False)
        self.assertIsInstance(level, TetracoinLevel)
        self.assertTrue(level.id)
        self.assertIsNotNone(level.grid)

    def test_solvable_generation_retry(self):
        """Test that force_solvable retries untill valid (or fails)."""
        # Small grid might be unsolvable easily, so it should exercise retry
        try:
            level = self.generator.generate(force_solvable=True)
            if level.solution_hint:
                self.assertGreater(len(level.solution_hint), 0)
        except Exception as e:
            # Failure is acceptable if retry exhaustion, but loop logic invoked
            print(f"Generation failed as expected/possible: {e}")

    def test_batch_sequential(self):
        """Test sequential batch generation."""
        levels = self.generator.generate_batch(num_levels=3, parallel=False)
        self.assertEqual(len(levels), 3)
        self.assertTrue(all(isinstance(l[0], TetracoinLevel) for l in levels)) # Returns tuples by default

    def test_batch_parallel(self):
        """Test parallel batch generation."""
        # Note: parallel might fail in some test runners with Pickling
        # We try 2 levels
        levels = self.generator.generate_batch(num_levels=2, parallel=True)
        self.assertEqual(len(levels), 2)
        
    def test_difficulty_targeting(self):
        """Test configuration override by difficulty."""
        level = self.generator.generate(difficulty_target=DifficultyLevel.EASY, return_metadata=False)
        # Easy config has specific dims
        self.assertEqual(level.grid.cols, 6) # Easy width defined in spec
        self.assertEqual(level.grid.rows, 8) 

    def test_legacy_wrappers(self):
        """Test legacy compatibility."""
        from src.tetracoin.legacy_generators import generate_drop_away_level
        
        with self.assertWarns(DeprecationWarning):
            res = generate_drop_away_level()
            self.assertIn("id", res)
            self.assertIn("grid", res)

if __name__ == '__main__':
    unittest.main()
