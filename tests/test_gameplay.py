import unittest
import pygame
from settings import *
from grid_manager import GridManager
from sprites import BlockSprite, CoinSprite
from game import Game

# Mock pygame for headless testing
class MockSprite(pygame.sprite.Sprite):
    def __init__(self, groups):
        self.groups = groups
        if groups:
            for group in groups:
                group.add(self)
    def kill(self):
        if self.groups:
            for group in self.groups:
                group.remove(self)

class TestGameplay(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1, 1)) # Minimal display for sprite init
        
        self.level_data = {
            "id": 1,
            "grid_cols": 5,
            "grid_rows": 5,
            "layout": [
                [1, 1, 1, 1, 1],
                [1, 0, 0, 0, 1],
                [1, 0, 0, 0, 1],
                [1, 0, 0, 0, 1],
                [1, 1, 1, 1, 1],
            ],
            "blocks": [],
            "coins": []
        }
        self.grid_manager = GridManager(self.level_data)
        self.all_sprites = pygame.sprite.Group()
        self.block_sprites = pygame.sprite.Group()
        self.coin_sprites = pygame.sprite.Group()

    def test_grid_bounds_and_walls(self):
        self.assertTrue(self.grid_manager.is_wall(0, 0)) # Wall
        self.assertFalse(self.grid_manager.is_wall(1, 1)) # Empty
        self.assertTrue(self.grid_manager.is_wall(-1, 0)) # Out of bounds
        self.assertFalse(self.grid_manager.is_valid_pos(5, 5)) # Out of bounds

    def test_block_movement(self):
        block_data = {"shape": "T", "color": "RED", "count": 1, "start_pos": (1, 1)}
        block = BlockSprite(block_data, [self.all_sprites, self.block_sprites])
        self.grid_manager.register_block(block)

        # Valid move
        self.assertTrue(self.grid_manager.try_move(block, 1, 0)) # Move Right to (2, 1)
        block.move(1, 0)
        self.assertEqual(block.grid_x, 2)
        self.assertEqual(block.grid_y, 1)

        # Invalid move (Wall)
        self.assertFalse(self.grid_manager.try_move(block, 0, -1)) # Move Up to (2, 0) which is wall

    def test_block_collision(self):
        block1_data = {"shape": "T", "color": "RED", "count": 1, "start_pos": (1, 1)}
        block1 = BlockSprite(block1_data, [self.all_sprites, self.block_sprites])
        self.grid_manager.register_block(block1)

        block2_data = {"shape": "T", "color": "BLUE", "count": 1, "start_pos": (2, 1)}
        block2 = BlockSprite(block2_data, [self.all_sprites, self.block_sprites])
        self.grid_manager.register_block(block2)

        # Try to move block1 into block2
        self.assertFalse(self.grid_manager.try_move(block1, 1, 0))

    def test_coin_collection(self):
        # Setup Game-like environment
        game = Game()
        # Override with our test data
        game.level_data = self.level_data
        game.grid_manager = self.grid_manager
        game.all_sprites = self.all_sprites
        game.block_sprites = self.block_sprites
        game.coin_sprites = self.coin_sprites
        
        # Add Block and Coin
        block_data = {"shape": "T", "color": "RED", "count": 1, "start_pos": (1, 1)}
        block = BlockSprite(block_data, [self.all_sprites, self.block_sprites])
        game.grid_manager.register_block(block)
        
        coin_data = {"color": "RED", "pos": (2, 1)}
        coin = CoinSprite(coin_data, [self.all_sprites, self.coin_sprites])

        # Move block to coin
        block.move(1, 0) # Now at (2, 1)
        
        # Check collection
        game.check_collection(block)
        
        self.assertEqual(block.counter, 0)
        self.assertFalse(coin.alive()) # Coin should be removed
        self.assertFalse(block.alive()) # Block should be removed (count 0)

if __name__ == '__main__':
    unittest.main()
