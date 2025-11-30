import unittest
import pygame
from settings import *
from game import Game
from data.levels import LEVEL_DATA

class TestGameLoop(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1, 1))
        self.game = Game()

    def test_level_loading(self):
        self.game.load_level(0)
        self.assertEqual(self.game.level_data['id'], 1)
        self.assertEqual(len(self.game.block_sprites), 1)
        self.assertEqual(len(self.game.coin_sprites), 1)

        self.game.load_level(1)
        self.assertEqual(self.game.level_data['id'], 2)
        self.assertEqual(len(self.game.block_sprites), 2)
        self.assertEqual(len(self.game.coin_sprites), 2)

    def test_win_condition(self):
        self.game.load_level(0)
        
        # Simulate clearing the level
        for block in self.game.block_sprites:
            block.kill()
        for coin in self.game.coin_sprites:
            coin.kill()
            
        self.game.check_win_condition()
        self.assertTrue(self.game.level_complete)

    def test_restart(self):
        self.game.load_level(0)
        # Modify state
        self.game.block_sprites.empty()
        self.assertEqual(len(self.game.block_sprites), 0)
        
        # Restart
        self.game.load_level(0)
        self.assertEqual(len(self.game.block_sprites), 1)

    def test_game_states(self):
        # Initial state should be Menu
        self.assertEqual(self.game.state, self.game.STATE_MENU)
        
        # Start game
        self.game.start_game()
        self.assertEqual(self.game.state, self.game.STATE_PLAY)
        self.assertEqual(self.game.current_level_index, 0)
        
        # Simulate beating all levels
        total_levels = len(LEVEL_DATA)
        self.game.load_level(total_levels) # Try to load index out of bounds
        
        self.assertEqual(self.game.state, self.game.STATE_VICTORY)

if __name__ == '__main__':
    unittest.main()
