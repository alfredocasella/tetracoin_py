import unittest
import pygame
from grid_manager import GridManager
from sprites import BlockSprite
from settings import *

class TestAdvancedFeatures(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_void_cells(self):
        level_data = {
            "id": 99,
            "grid_cols": 3,
            "grid_rows": 3,
            "layout": [
                [2, 0, 2], # Void, Empty, Void
                [0, 0, 0],
                [2, 0, 2]
            ],
            "blocks": [],
            "coins": []
        }
        gm = GridManager(level_data)
        
        # Check Void
        self.assertFalse(gm.is_valid_pos(0, 0)) # Void
        self.assertTrue(gm.is_valid_pos(1, 0))  # Empty
        self.assertFalse(gm.is_valid_pos(2, 0)) # Void
        
        # Check Wall (Void is not a wall, but is invalid)
        self.assertFalse(gm.is_wall(0, 0)) 

    def test_drag_logic(self):
        block_data = {"shape": "T", "color": "RED", "count": 1, "start_pos": (1, 1)}
        block = BlockSprite(block_data, [])
        
        # Start Drag
        block.dragging = True
        block.rect.x = 100
        
        # Update should NOT interpolate when dragging
        block.update()
        self.assertEqual(block.rect.x, 100)
        
        # Stop Drag
        block.dragging = False
        block.target_x = 200
        
        # Update SHOULD interpolate now
        block.update()
        self.assertEqual(block.rect.x, 110) # 100 + speed(10)

if __name__ == '__main__':
    unittest.main()
