import unittest
import sys
import os
import random

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tetracoin.coin_placer import CoinPlacer, DifficultyLevel
from src.tetracoin.spec import GridState, EntityType, ColorType, PiggyBank, Coin

class TestCoinPlacer(unittest.TestCase):
    
    def setUp(self):
        self.placer = CoinPlacer(rng=random)
        self.grid = GridState(rows=10, cols=5)
        # Add basic piggybanks
        self.p1 = PiggyBank(id="p1", row=9, col=0, color=ColorType.RED, capacity=10)
        self.p2 = PiggyBank(id="p2", row=9, col=2, color=ColorType.BLUE, capacity=10)
        self.grid.entities.extend([self.p1, self.p2])
        
    def test_distribute_coins_to_colors(self):
        """Test random distribution of coin colors."""
        definitions = self.placer._distribute_coins_to_colors(4, [self.p1, self.p2])
        self.assertEqual(len(definitions), 4)
        reds = definitions.count(ColorType.RED)
        blues = definitions.count(ColorType.BLUE)
        self.assertEqual(reds, 2)
        self.assertEqual(blues, 2)
        
    def test_place_easy_success(self):
        """Easy mode should place coins in the same column as piggybanks if possible."""
        # Ensure columns 0 and 2 are empty
        success = self.placer.place_coins_strategic(self.grid, num_coins=2, difficulty=1)
        self.assertTrue(success)
        
        coins = [e for e in self.grid.entities if e.type == EntityType.COIN]
        self.assertEqual(len(coins), 2)
        
        for c in coins:
            # In EASY, finding a coin in a matching column is prioritized.
            # With ample space, it should ALWAYS be in matching column.
            target_pb = self.p1 if c.color == ColorType.RED else self.p2
            self.assertEqual(c.col, target_pb.col, "Easy mode should place coin in same column as piggybank")
            
    def test_place_expert_flexibility(self):
        """Expert mode should be able to place coins even if direct columns are full/blocked, by using others."""
        # Block direct columns 0 and 2
        # Fill them with dummy coins or obstacles
        for r in range(9):
             self.grid.entities.append(Coin(id=f"dummy_0_{r}", row=r, col=0, color=ColorType.RED))
             self.grid.entities.append(Coin(id=f"dummy_2_{r}", row=r, col=2, color=ColorType.BLUE))
             
        # Try to place RED coin. Direct column 0 is full.
        # Expert mode should try other columns.
        success = self.placer.place_coins_strategic(self.grid, num_coins=1, difficulty=10)
        self.assertTrue(success, "Expert mode should find alternative columns")
        
        new_coins = [e for e in self.grid.entities if e.type == EntityType.COIN and "dummy" not in e.id]
        self.assertEqual(len(new_coins), 1)
        # Should be in col 1, 3, or 4
        self.assertIn(new_coins[0].col, [1, 3, 4])

if __name__ == '__main__':
    unittest.main()
