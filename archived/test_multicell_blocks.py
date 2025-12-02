import unittest
import pygame
from game import Game
from sprites import BlockSprite, SHAPES

class TestMultiCellBlocks(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1, 1))
    
    def test_shape_definitions(self):
        """Verify all Tetris shapes are defined"""
        self.assertIn('I2', SHAPES)
        self.assertIn('L4', SHAPES)
        self.assertIn('T4', SHAPES)
        self.assertEqual(len(SHAPES['I2']), 2)
        self.assertEqual(len(SHAPES['L4']), 4)
    
    def test_block_occupied_cells(self):
        """Test that blocks correctly report all occupied cells"""
        block_data = {
            'shape': 'L4',
            'color': 'RED',
            'count': 1,
            'start_pos': (2, 2)
        }
        block = BlockSprite(block_data, [])
        
        occupied = block.get_occupied_cells()
        # L4 at (2,2) should occupy (2,2), (2,3), (2,4), (3,4)
        expected = [(2, 2), (2, 3), (2, 4), (3, 4)]
        self.assertEqual(set(occupied), set(expected))
    
    def test_multi_cell_movement(self):
        """Test that multi-cell blocks can move multiple cells"""
        game = Game()
        game.use_json_levels = False
        game.start_game()
        
        # Get first block
        if len(game.block_sprites) > 0:
            block = game.block_sprites.sprites()[0]
            original_x = block.grid_x
            
            # Try to move 3 cells (should work if space is available)
            if game.grid_manager.try_move(block, 3, 0):
                block.move(3, 0)
                self.assertEqual(block.grid_x, original_x + 3)

if __name__ == '__main__':
    unittest.main()
