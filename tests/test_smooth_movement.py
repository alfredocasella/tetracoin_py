import unittest
import pygame
from settings import *
from sprites import BlockSprite

class TestSmoothMovement(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1, 1))
        
        self.block_data = {"shape": "T", "color": "RED", "count": 1, "start_pos": (0, 0)}
        self.block = BlockSprite(self.block_data, [])

    def test_interpolation(self):
        # Initial pos
        start_x = GRID_OFFSET_X
        self.assertEqual(self.block.rect.x, start_x)
        self.assertEqual(self.block.target_x, start_x)
        
        # Move logic (simulated)
        self.block.move(1, 0) # Move right 1 tile
        target_x = GRID_OFFSET_X + TILE_SIZE
        
        self.assertEqual(self.block.target_x, target_x)
        self.assertNotEqual(self.block.rect.x, target_x) # Should not be there yet
        
        # Update loop simulation
        # Speed is 10
        self.block.update()
        self.assertEqual(self.block.rect.x, start_x + 10)
        
        # Fast forward
        for _ in range(10):
            self.block.update()
            
        self.assertEqual(self.block.rect.x, target_x) # Should be there now

if __name__ == '__main__':
    unittest.main()
