import unittest
import pygame
from game import Game
from settings import *

class TestGDD3Core(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1, 1))
        self.game = Game()

    def test_coin_queue_logic(self):
        # Setup a level with a queue
        level_data = {
            "id": 99,
            "grid_cols": 3,
            "grid_rows": 3,
            "layout": [[0]*3]*3,
            "blocks": [],
            "coins": {
                "static": [],
                "queues": [
                    {"pos": (1, 1), "items": ["RED", "BLUE"]}
                ]
            }
        }
        
        # Manually load this level data
        # We need to mock LEVEL_DATA or just inject it
        self.game.level_data = level_data
        from grid_manager import GridManager
        self.game.grid_manager = GridManager(level_data)
        # Actually easier to just use the game's load_level if we can inject data.
        # Let's monkeypatch LEVEL_DATA in game module for this test
        import game
        game.LEVEL_DATA = [level_data]
        self.game.load_level(0)
        
        # 1. Verify first coin spawned
        self.assertEqual(len(self.game.coin_sprites), 1)
        coin = self.game.coin_sprites.sprites()[0]
        self.assertEqual(coin.coin_data['color'], "RED")
        
        # 2. Collect it
        coin.kill()
        self.game.check_pending_spawns()
        
        # 3. Verify second coin spawned
        self.assertEqual(len(self.game.coin_sprites), 1)
        coin = self.game.coin_sprites.sprites()[0]
        self.assertEqual(coin.coin_data['color'], "BLUE")

    def test_spawn_paradox(self):
        # Setup: Queue at (1,1) with [RED]. Blue Block at (1,1).
        level_data = {
            "id": 98,
            "grid_cols": 3,
            "grid_rows": 3,
            "layout": [[0]*3]*3,
            "blocks": [
                {"shape": "I", "color": "BLUE", "count": 1, "start_pos": (1, 1)}
            ],
            "coins": {
                "static": [],
                "queues": [
                    {"pos": (1, 1), "items": ["RED"]}
                ]
            }
        }
        import game
        game.LEVEL_DATA = [level_data]
        self.game.load_level(0)
        
        # 1. Verify NO coin spawned (blocked by Blue block)
        self.assertEqual(len(self.game.coin_sprites), 0)
        
        # 2. Move Blue block away
        block = self.game.block_sprites.sprites()[0]
        self.game.grid_manager.try_move(block, 1, 0)
        block.move(1, 0)
        self.game.check_pending_spawns()
        
        # 3. Verify Red coin spawns now
        self.assertEqual(len(self.game.coin_sprites), 1)
        self.assertEqual(self.game.coin_sprites.sprites()[0].coin_data['color'], "RED")

if __name__ == '__main__':
    unittest.main()
