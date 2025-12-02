class GridManager:
    def __init__(self, level_data):
        self.cols = level_data['grid_cols']
        self.rows = level_data['grid_rows']
        self.layout = level_data['layout']
        self.blocks = [] # List of BlockSprite objects

    def register_block(self, block):
        self.blocks.append(block)

    def is_wall(self, x, y):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.layout[y][x] == 1
        return True # Out of bounds is a wall
    
    def is_valid_pos(self, x, y):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            # Check for Void (2)
            if self.layout[y][x] == 2:
                return False
            return True
        return False

    def get_block_at(self, x, y):
        """Check if any block occupies the given cell"""
        for block in self.blocks:
            if (x, y) in block.get_occupied_cells():
                return block
        return None

    def try_move(self, block, dx, dy):
        """Check if block can move by dx, dy (can be multi-cell move)"""
        new_x = block.grid_x + dx
        new_y = block.grid_y + dy
        
        # Check all cells of the block in new position
        for cell_dx, cell_dy in block.shape_cells:
            check_x = new_x + cell_dx
            check_y = new_y + cell_dy
            
            # 1. Check bounds and walls
            if not self.is_valid_pos(check_x, check_y) or self.is_wall(check_x, check_y):
                return False
            
            # 2. Check for other blocks (excluding self)
            other_block = self.get_block_at(check_x, check_y)
            if other_block and other_block != block:
                return False
            
            # 3. Check for coins of different color (they act as obstacles)
            from core.game import Game  # Import here to avoid circular dependency
            if hasattr(self, '_game_ref'):
                for coin in self._game_ref.coin_sprites:
                    if coin.grid_x == check_x and coin.grid_y == check_y:
                        # Coin acts as obstacle if different color
                        if coin.coin_data['color'] != block.block_data['color']:
                            return False
                
        return True
    
    def has_valid_moves(self):
        """Check if any block can move in any direction (deadlock detection)"""
        for block in self.blocks:
            # Try all 4 directions
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                if self.try_move(block, dx, dy):
                    return True
        return False
