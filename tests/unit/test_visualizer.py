import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.tetracoin.spec import GridState, EntityType, Coin, Obstacle, PiggyBank, ColorType
from src.tetracoin.visualization import TetracoinVisualizer

class TestTetracoinVisualizer(unittest.TestCase):
    def test_render_basic_grid(self):
        """Test rendering of a simple grid with entities."""
        grid = GridState(rows=5, cols=5)
        # Add coin
        grid.entities.append(Coin(id="c1", row=2, col=2, color=ColorType.YELLOW))
        # Add obstacle
        grid.entities.append(Obstacle(id="o1", row=2, col=3, color=ColorType.GRAY))
        # Add PiggyBank
        grid.entities.append(PiggyBank(id="p1", row=4, col=2, color=ColorType.RED, capacity=5))
        
        output = TetracoinVisualizer.render_static(grid)
        print("\n" + output)
        
        self.assertIn("Grid: 5x5", output)
        self.assertIn("©", output) # Coin
        self.assertIn("#", output) # Obstacle
        self.assertIn("U", output) # Piggy
        self.assertIn("|.....|", output) # Empty row

    def test_render_empty_grid(self):
        """Test rendering empty grid."""
        grid = GridState(rows=3, cols=3)
        output = TetracoinVisualizer.render_static(grid)
        self.assertIn("Grid: 3x3", output)
        
    def test_invalid_input(self):
        """Test invalid input handling."""
        output = TetracoinVisualizer.render_static(None)
        self.assertIn("Invalid Level", output)

if __name__ == '__main__':
    unittest.main()
