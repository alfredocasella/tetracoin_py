import unittest
import pygame
from game import Game
from grid_manager import GridManager
from settings import *

class TestGDD4Features(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1, 1))
        self.game = Game()

    def test_deadlock_detection(self):
        # Create a level where blocks cannot move
        level_data = {
            "id": 97,
            "grid_cols": 3,
            "grid_rows": 3,
            "layout": [
                [1, 1, 1],
                [1, 0, 1],
                [1, 1, 1]
            ],
            "blocks": [
                {"shape": "I", "color": "RED", "count": 1, "start_pos": (1, 1)}
            ],
            "coins": {
                "static": [],
                "queues": []
            },
            "stars_thresholds": [1, 2, 3]
        }
        
        import game
        game.LEVEL_DATA = [level_data]
        self.game.load_level(0)
        
        # Verify has_valid_moves returns False
        self.assertFalse(self.game.grid_manager.has_valid_moves())
        
        # Trigger deadlock check
        self.game.check_deadlock()
        
        # Verify deadlock flag is set
        self.assertTrue(self.game.is_deadlocked)

    def test_stars_calculation(self):
        # Create a simple level
        level_data = {
            "id": 96,
            "grid_cols": 3,
            "grid_rows": 3,
            "layout": [[0]*3]*3,
            "blocks": [
                {"shape": "I", "color": "RED", "count": 1, "start_pos": (0, 0)}
            ],
            "coins": {
                "static": [
                    {"color": "RED", "pos": (2, 2)}
                ],
                "queues": []
            },
            "stars_thresholds": [3, 5, 8]
        }
        
        import game
        game.LEVEL_DATA = [level_data]
        self.game.load_level(0)
        
        # Simulate moves
        self.game.move_count = 2
        
        # Manually trigger win condition
        self.game.block_sprites.empty()
        self.game.coin_sprites.empty()
        self.game.check_win_condition()
        
        # Verify 3 stars (2 moves <= 3)
        self.assertEqual(self.game.stars_earned, 3)
        
        # Test 2 stars
        self.game.level_complete = False
        self.game.move_count = 4
        self.game.check_win_condition()
        self.assertEqual(self.game.stars_earned, 2)
        
        # Test 1 star
        self.game.level_complete = False
        self.game.move_count = 7
        self.game.check_win_condition()
        self.assertEqual(self.game.stars_earned, 1)
        
        # Test 0 stars
        self.game.level_complete = False
        self.game.move_count = 10
        self.game.check_win_condition()
        self.assertEqual(self.game.stars_earned, 0)

if __name__ == '__main__':
    unittest.main()
