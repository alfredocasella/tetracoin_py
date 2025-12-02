import unittest
import json
import os
from level_loader import LevelLoader

class TestLevelLoader(unittest.TestCase):
    def setUp(self):
        self.loader = LevelLoader()
    
    def test_level_count(self):
        """Verify we have 300 levels"""
        self.assertEqual(self.loader.get_level_count(), 300)
    
    def test_load_tutorial_level(self):
        """Test loading a hand-crafted tutorial level"""
        level = self.loader.load_level(1)
        
        # Verify basic structure
        self.assertEqual(level['id'], 1)
        self.assertEqual(level['grid_cols'], 6)
        self.assertEqual(level['grid_rows'], 6)
        
        # Verify blocks
        self.assertEqual(len(level['blocks']), 1)
        self.assertEqual(level['blocks'][0]['color'], 'RED')
        self.assertEqual(level['blocks'][0]['count'], 3)
        
        # Verify coins
        self.assertEqual(len(level['coins']['static']), 3)
    
    def test_load_generated_level(self):
        """Test loading a procedurally generated level"""
        level = self.loader.load_level(50)
        
        # Verify it loaded successfully
        self.assertIsNotNone(level)
        self.assertEqual(level['id'], 50)
        
        # Verify it has blocks and coins
        self.assertGreater(len(level['blocks']), 0)
        self.assertGreater(len(level['coins']['static']), 0)
    
    def test_cache(self):
        """Verify caching works"""
        level1 = self.loader.load_level(1)
        level1_again = self.loader.load_level(1)
        
        # Should be the same object (cached)
        self.assertIs(level1, level1_again)

if __name__ == '__main__':
    unittest.main()
