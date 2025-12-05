import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tetracoin.difficulty import TetracoinDifficultyAnalyzer, DifficultyMetrics, DifficultyTier
from src.tetracoin.spec import GridState, EntityType, ColorType, Coin, Obstacle
from src.tetracoin.solver import Move

class TestTetracoinDifficulty(unittest.TestCase):
    
    def setUp(self):
        self.grid = GridState(rows=10, cols=10)
        # Add some coins
        for i in range(5):
            self.grid.entities.append(Coin(id=f"c{i}", row=i, col=0, color=ColorType.RED))
            
    def test_basic_metrics(self):
        """Test calculation of raw metrics."""
        # Add some movable blocks for routing/deception
        obs1 = Obstacle(id="obs1", row=1, col=1, color=ColorType.GRAY)
        obs2 = Obstacle(id="obs2", row=1, col=2, color=ColorType.GRAY)
        self.grid.entities.extend([obs1, obs2])
        
        # Fake solution path
        path = [
            Move("obs1", "LEFT"),
            Move("obs1", "RIGHT")
        ]
        
        metrics = TetracoinDifficultyAnalyzer._measure(self.grid, path)
        
        self.assertEqual(metrics.collection, 5)
        self.assertEqual(metrics.moves, 2)
        # 2 movable blocks * 2 length = 4. Scaled by //4 = 1.
        # Wait, my logic was raw: routing_nodes // 4.
        # routing_nodes = 2 * 2 = 4. 4 // 4 = 1.
        self.assertEqual(metrics.routing, 1)
        
        # All movable are 2. Used "obs1". "obs2" unused. Deception should be 1.
        self.assertEqual(metrics.deception, 1)
        
    def test_tier_mapping(self):
        """Test score to tier mapping."""
        # Fake metrics that should result in EASY
        metrics_easy = DifficultyMetrics(collection=5, routing=5, moves=5, deception=1)
        _, score_easy = TetracoinDifficultyAnalyzer._normalise_and_score(metrics_easy)
        tier_easy = TetracoinDifficultyAnalyzer._tier_for(score_easy)
        self.assertEqual(tier_easy, DifficultyTier.EASY)
        
        # Fake metrics that should result in HARD/EXPERT
        # Max caps: collection=20, routing=50, moves=25, deception=10
        metrics_hard = DifficultyMetrics(collection=25, routing=60, moves=30, deception=12)
        _, score_hard = TetracoinDifficultyAnalyzer._normalise_and_score(metrics_hard)
        # Should be near 100
        tier_hard = TetracoinDifficultyAnalyzer._tier_for(score_hard)
        self.assertTrue(tier_hard in (DifficultyTier.HARD, DifficultyTier.EXPERT))

if __name__ == '__main__':
    unittest.main()
