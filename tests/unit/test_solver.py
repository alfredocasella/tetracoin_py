import unittest
import sys
import os
import random

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.tetracoin.solver import TetracoinSolver, GameState
from src.tetracoin.spec import GridState, EntityType, ColorType, PiggyBank, Coin, Obstacle

class TestTetracoinSolver(unittest.TestCase):
    
    def setUp(self):
        self.grid = GridState(rows=10, cols=5)
        self.p1 = PiggyBank(id="p1", row=9, col=2, color=ColorType.RED)
        self.grid.entities.append(self.p1)
        
    def test_solve_simple(self):
        """Test solving a trivial case: Coin directly above PiggyBank."""
        # Coin at (5, 2), PiggyBank at (9, 2). Gravity solves it instantly?
        # If gravity is part of "apply_move", we need at least ONE move to trigger physics?
        # NO, apply_move applies a PLAYER move. Gravity happens AFTER.
        # But if the initial state has falling coins, does solver handle it?
        # Solver assumes "Turn Based". Start state -> Player Move -> Physics -> End State.
        # Ideally, we should run physics on Initial State first.
        # But Solver.solve_bfs checks `initial_state.is_winning()`.
        # If we just place a coin in mid-air, it won't be collected until physics runs.
        # So Solver should probably run physics on init?
        # However, `GameState` just wraps grid.
        
        # Scenario: Coin is BLOCKED by Obstacle. Player moves obstacle. Coin Falls.
        self.grid.entities.append(Coin(id="c1", row=5, col=2, color=ColorType.RED))
        obs = Obstacle(id="obs1", row=7, col=2, color=ColorType.GRAY) # Blocks path
        self.grid.entities.append(obs)
        
        # Only space to move Obstacle is Left (col 1) or Right (col 3)
        # (Assuming rows 7,1 and 7,3 empty).
        
        found, steps, moves = TetracoinSolver.solve_bfs(self.grid, max_depth=5)
        self.assertTrue(found, "Should find solution by moving obstacle")
        self.assertGreater(steps, 0)
        
        # Check first move involves obstacles
        self.assertEqual(moves[0].entity_id, "obs1")
        
    def test_unsolvable(self):
        """Test impossible scenario."""
        # Coin blocked by FIXED block (immovable)
        from src.tetracoin.spec import FixedBlock
        self.grid.entities.append(Coin(id="c2", row=5, col=2, color=ColorType.RED))
        fb = FixedBlock(id="fix1", row=7, col=2, color=ColorType.GRAY)
        self.grid.entities.append(fb)
        
        found, _, _ = TetracoinSolver.solve_bfs(self.grid, max_depth=5)
        self.assertFalse(found, "Should be unsolvable with FixedBlock")

if __name__ == '__main__':
    unittest.main()
