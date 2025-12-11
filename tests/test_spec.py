import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tetracoin.spec import GridState, PhysicsEngine, EntityType, ColorType, Coin, PiggyBank, Obstacle

class TestTetracoinSpec(unittest.TestCase):
    def setUp(self):
        self.state = GridState(rows=5, cols=5)

    def test_entity_creation(self):
        coin = Coin(id="c1", row=0, col=0, color=ColorType.RED)
        self.assertEqual(coin.type, EntityType.COIN)
        self.assertEqual(coin.color, ColorType.RED)
        
    def test_grid_occupancy(self):
        coin = Coin(id="c1", row=2, col=2, color=ColorType.RED)
        self.state.entities.append(coin)
        
        self.assertIsNotNone(self.state.get_entity_at(2, 2))
        self.assertIsNone(self.state.get_entity_at(0, 0))
        self.assertFalse(self.state.is_empty(2, 2))
        self.assertTrue(self.state.is_empty(0, 0))

    def test_gravity_free_fall(self):
        # Coin at (0, 0)
        coin = Coin(id="c1", row=0, col=0, color=ColorType.RED)
        self.state.entities.append(coin)
        
        # Update physics
        PhysicsEngine.update(self.state)
        
        # Should have fallen to (1, 0)
        self.assertEqual(coin.row, 1)
        self.assertTrue(coin.is_falling)
        
        # Update again
        PhysicsEngine.update(self.state)
        self.assertEqual(coin.row, 2)

    def test_floor_collision(self):
        # Coin at bottom (4, 0)
        coin = Coin(id="c1", row=4, col=0, color=ColorType.RED)
        self.state.entities.append(coin)
        
        PhysicsEngine.update(self.state)
        
        # Should stay at (4, 0) and stop falling
        self.assertEqual(coin.row, 4)
        self.assertFalse(coin.is_falling)

    def test_piggybank_collection(self):
        # Coin above PiggyBank
        coin = Coin(id="c1", row=0, col=0, color=ColorType.RED)
        piggy = PiggyBank(id="p1", row=1, col=0, color=ColorType.RED, capacity=5)
        
        self.state.entities.append(coin)
        self.state.entities.append(piggy)
        
        # Update
        _, events = PhysicsEngine.update(self.state)
        
        # Coin should be collected
        self.assertTrue(coin.is_collected)
        self.assertEqual(piggy.current_count, 1)
        self.assertIn("COLLECT_RED", events)

    def test_piggybank_mismatch(self):
        # Red Coin above Blue PiggyBank
        coin = Coin(id="c1", row=0, col=0, color=ColorType.RED)
        piggy = PiggyBank(id="p1", row=1, col=0, color=ColorType.BLUE)
        
        self.state.entities.append(coin)
        self.state.entities.append(piggy)
        
        PhysicsEngine.update(self.state)
        
        # Coin blocked
        self.assertEqual(coin.row, 0)
        self.assertFalse(coin.is_collected)
        self.assertEqual(piggy.current_count, 0)
        self.assertFalse(coin.is_falling)

if __name__ == '__main__':
    unittest.main()
