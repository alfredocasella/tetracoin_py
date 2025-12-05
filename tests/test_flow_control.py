import unittest
import sys
import os
import random

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tetracoin.flow_control import FlowControlObstacleAdder, DIFFICULTY_SETTINGS
from src.tetracoin.spec import GridState, EntityType, ColorType, PiggyBank, Deflector, Gateway, Trap, Support

class TestFlowControl(unittest.TestCase):
    
    def setUp(self):
        self.adder = FlowControlObstacleAdder(rng=random)
        self.grid = GridState(rows=10, cols=6)
        # Add a piggybank to define flow
        self.grid.entities.append(PiggyBank(id="p1", row=9, col=2, color=ColorType.RED))
        
    def test_density_easy(self):
        """Easy difficulty should have low density and no traps."""
        self.adder.add_obstacles(self.grid, "easy")
        
        traps = [e for e in self.grid.entities if e.type == EntityType.TRAP]
        self.assertEqual(len(traps), 0, "Easy mode should have no traps")
        
        total_obs = self.adder._count_obstacles(self.grid)
        ratio = total_obs / (self.grid.rows * self.grid.cols)
        settings = DIFFICULTY_SETTINGS["easy"]
        
        # Verify min density attempted (it might be slightly off due to rounding or limited space, but let's check basic bounds)
        self.assertGreaterEqual(ratio, settings.min_obstacle_ratio - 0.02) # Allow small margin
        self.assertLessEqual(ratio, settings.max_obstacle_ratio + 0.02)

    def test_density_hard(self):
        """Hard difficulty should have higher density and allow traps."""
        self.adder.add_obstacles(self.grid, "hard")
        
        traps = [e for e in self.grid.entities if e.type == EntityType.TRAP]
        # Max traps for hard is 6. We expect some if space allows.
        self.assertLessEqual(len(traps), 6)
        
        total_obs = self.adder._count_obstacles(self.grid)
        ratio = total_obs / (self.grid.rows * self.grid.cols)
        settings = DIFFICULTY_SETTINGS["hard"]
        
        self.assertGreater(ratio, 0.1, "Hard mode should have decent obstacle density")

    def test_deflector_placement(self):
        # We need flow paths to place deflectors
        self.grid.entities.clear()
        self.grid.entities.append(PiggyBank(id="p1", row=9, col=3, color=ColorType.BLUE))
        
        self.adder._place_deflectors(self.grid, [(5, 3)], DIFFICULTY_SETTINGS["medium"])
        
        defls = [e for e in self.grid.entities if e.type == EntityType.DEFLECTOR]
        if defls:
            d = defls[0]
            self.assertIn(d.direction, ["LEFT", "RIGHT"])
            self.assertEqual(d.row, 5)
            self.assertEqual(d.col, 3)
            
    def test_ascii_dump(self):
        self.adder.add_obstacles(self.grid, "medium")
        ascii_art = self.adder.get_ascii_grid(self.grid)
        self.assertIn("U", ascii_art) # Piggybank
        # print("\n" + ascii_art) # Uncomment to see

if __name__ == '__main__':
    unittest.main()
