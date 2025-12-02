import pygame
from core.settings import *
from data.levels import LEVEL_DATA
from core.grid_manager import GridManager
from core.sprites import BlockSprite, CoinSprite
from ui.ui import UI
from core.audio_manager import AudioManager
from core.level_loader import LevelLoader
from core.save_system import SaveSystem

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TetraCoin")
        self.clock = pygame.time.Clock()
        self.running = True
        self.ui = UI()
        self.audio_manager = AudioManager()
        self.audio_manager.play_bgm()
        
        # Level loading system
        self.level_loader = LevelLoader()
        self.use_json_levels = True  # Toggle to use JSON levels
        
        # Save system
        self.save_system = SaveSystem()
        
        self.STATE_MENU = 0
        self.STATE_PLAY = 1
        self.STATE_VICTORY = 2
        self.STATE_DEFEAT = 3
        
        self.state = self.STATE_MENU
        self.current_level_index = 0
        self.gold_earned_this_level = 0

    def start_game(self):
        self.state = self.STATE_PLAY
        self.load_level(self.current_level_index)

    def load_level(self, level_index):
        # Load from JSON or Python data
        if self.use_json_levels:
            try:
                self.level_data = self.level_loader.load_level(level_index + 1)
            except FileNotFoundError:
                print(f"JSON level {level_index + 1} not found")
                # Check if we've run out of levels
                if level_index + 1 > self.level_loader.get_level_count():
                    # All levels completed, return to menu
                    self.state = self.STATE_MENU
                    return
                # Try Python data as fallback
                try:
                    if level_index < len(LEVEL_DATA):
                        self.level_data = LEVEL_DATA[level_index]
                    else:
                        self.state = self.STATE_MENU
                        return
                except:
                    self.state = self.STATE_MENU
                    return
        else:
            if level_index >= len(LEVEL_DATA):
                # All levels completed
                self.state = self.STATE_MENU
                return
            self.level_data = LEVEL_DATA[level_index]
            
        self.grid_manager = GridManager(self.level_data)
        self.grid_manager._game_ref = self  # Store reference for coin collision check
        
        # Calculate dynamic grid offset to center it in the GRID_AREA
        # Dynamic Tile Size Calculation
        max_grid_width = SCREEN_WIDTH - 20 # 10px margin on each side
        max_grid_height = GRID_AREA_HEIGHT - 20 # 10px margin top/bottom
        
        # Calculate max possible tile size to fit width and height
        tile_size_w = max_grid_width // self.level_data['grid_cols']
        tile_size_h = max_grid_height // self.level_data['grid_rows']
        
        # Use the smaller of the two, but cap at default TILE_SIZE
        self.tile_size = min(TILE_SIZE, tile_size_w, tile_size_h)
        
        grid_pixel_width = self.level_data['grid_cols'] * self.tile_size
        grid_pixel_height = self.level_data['grid_rows'] * self.tile_size
        
        # Center horizontally
        global GRID_OFFSET_X, GRID_OFFSET_Y
        GRID_OFFSET_X = (SCREEN_WIDTH - grid_pixel_width) // 2
        
        # Center vertically in the available Grid Area
        available_height = GRID_AREA_HEIGHT
        GRID_OFFSET_Y = TOP_HUD_HEIGHT + (available_height - grid_pixel_height) // 2
        
        # Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.block_sprites = pygame.sprite.Group()
        self.coin_sprites = pygame.sprite.Group()
        
        # Create Block Sprites
        for block_data in self.level_data['blocks']:
            block = BlockSprite(block_data, [self.all_sprites, self.block_sprites], 
                              grid_offsets=(GRID_OFFSET_X, GRID_OFFSET_Y), tile_size=self.tile_size)
            
            # Validate block fits within grid
            for cell_x, cell_y in block.get_occupied_cells():
                if not (0 <= cell_x < self.level_data['grid_cols'] and 
                        0 <= cell_y < self.level_data['grid_rows']):
                    print(f"WARNING: Block {block_data.get('id', '?')} at {block_data['start_pos']} " +
                          f"with shape {block_data.get('shape', 'I2')} extends outside grid bounds!")
                    print(f"  Cell ({cell_x}, {cell_y}) is out of bounds ({self.level_data['grid_cols']}x{self.level_data['grid_rows']})")
            
            self.grid_manager.register_block(block)
            
        # Create Coin Sprites
        self.coin_queues = [] # List of dicts: {'pos': (x,y), 'items': ['RED', 'BLUE']}
        
        # Handle new coin format (dict) vs old (list) for backward compatibility if needed
        coins_data = self.level_data['coins']
        if isinstance(coins_data, list):
             # Legacy format
             for coin_data in coins_data:
                CoinSprite(coin_data, [self.all_sprites, self.coin_sprites],
                         grid_offsets=(GRID_OFFSET_X, GRID_OFFSET_Y), tile_size=self.tile_size)
        else:
            # New format
            for coin_data in coins_data.get('static', []):
                CoinSprite(coin_data, [self.all_sprites, self.coin_sprites],
                         grid_offsets=(GRID_OFFSET_X, GRID_OFFSET_Y), tile_size=self.tile_size)
            
            for queue_data in coins_data.get('queues', []):
                # Deep copy to avoid modifying level data
                self.coin_queues.append({
                    'pos': queue_data['pos'],
                    'items': list(queue_data['items'])
                })
                # Spawn first item if available
                self.process_coin_queue(self.coin_queues[-1])

        self.pending_spawns = [] # List of {'pos': (x,y), 'color': 'RED'}
        
        self.selected_block = None
        self.start_time = pygame.time.get_ticks()
        self.level_complete = False
        self.level_complete_time = 0
        self.move_count = 0
        self.is_deadlocked = False
        self.coins_collected_per_color = {} # Reset tracker
        self.preview_valid = False
        self.preview_pos = None
        self.stars_earned = 0  # Initialize stars
        self.gold_earned_this_level = 0  # Initialize gold
        
        # Timer & Lives
        self.time_limit = self.level_data.get('time_limit', 180) # Default 3 mins
        self.lives = 5 # Should load from save system
        self.timer_state = "NORMAL" # NORMAL, WARNING, CRITICAL

    def process_coin_queue(self, queue):
        if not queue['items']:
            return
            
        # Peek next item
        next_color = queue['items'][0]
        pos = queue['pos']
        
        # Check if space is free or occupied
        block_at_pos = self.grid_manager.get_block_at(pos[0], pos[1])
        
        if block_at_pos:
            # SPAWN PARADOX
            if block_at_pos.block_data['color'] == next_color:
                # Same color: Instant Collect!
                queue['items'].pop(0) # Remove from queue
                block_at_pos.counter -= 1
                block_at_pos.update_appearance()
                self.audio_manager.play_collect()
                
                if block_at_pos.counter <= 0:
                    block_at_pos.kill()
                    if self.selected_block == block_at_pos:
                        self.selected_block = None
                    if block_at_pos in self.grid_manager.blocks:
                        self.grid_manager.blocks.remove(block_at_pos)
                
                # Recursively process queue
                self.process_coin_queue(queue)
            else:
                # Different color: Pending Spawn
                # Do nothing, wait for block to move away.
                # We need to track that this queue is blocked? 
                # Actually, we can just check queues/pending spawns after every move.
                pass
        else:
            # Space free: Spawn normally
            color = queue['items'].pop(0)
            CoinSprite({'color': color, 'pos': pos}, [self.all_sprites, self.coin_sprites],
                     grid_offsets=(GRID_OFFSET_X, GRID_OFFSET_Y), tile_size=self.tile_size)

    def check_pending_spawns(self):
        # Check all queues to see if they can spawn now
        for queue in self.coin_queues:
            # If queue has items and NO coin at that pos
            if queue['items']:
                pos = queue['pos']
                # Check if a coin already exists there (spawned)
                coin_exists = False
                for coin in self.coin_sprites:
                    if coin.grid_x == pos[0] and coin.grid_y == pos[1]:
                        coin_exists = True
                        break
                
                if not coin_exists:
                    self.process_coin_queue(queue)

    def handle_input(self, event):
        # ... (Input handling code remains mostly same, but we need to call check_pending_spawns after moves)
        if self.state == self.STATE_MENU:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.start_game()
        
        elif self.state == self.STATE_VICTORY:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                # Check if there are more levels
                try:
                    next_level_index = self.current_level_index + 1
                    # Try to load next level
                    if self.use_json_levels:
                        # Check if level exists
                        next_level_num = next_level_index + 1
                        max_levels = self.level_loader.get_level_count()
                        if next_level_num > max_levels:
                            # No more levels, return to menu
                            print(f"All levels completed! (max: {max_levels})")
                            self.state = self.STATE_MENU
                            return
                    else:
                        # Check Python levels
                        if next_level_index >= len(LEVEL_DATA):
                            print(f"All levels completed! (max: {len(LEVEL_DATA)})")
                            self.state = self.STATE_MENU
                            return
                    
                    # Load next level
                    self.current_level_index = next_level_index
                    # Reset state before loading
                    self.level_complete = False
                    self.state = self.STATE_PLAY
                    self.load_level(self.current_level_index)
                except (FileNotFoundError, IndexError, Exception) as e:
                    # No more levels available or error loading
                    print(f"Error loading next level: {e}")
                    self.state = self.STATE_MENU
        elif self.state == self.STATE_DEFEAT:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Retry
                    self.load_level(self.current_level_index)
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    # Return to menu
                    self.state = self.STATE_MENU
        
        elif self.state == self.STATE_PLAY:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.load_level(self.current_level_index)
                    return

            if self.level_complete:
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.current_level_index += 1
                    self.load_level(self.current_level_index)
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    mx, my = pygame.mouse.get_pos()
                    # Convert to grid coordinates
                    gx = (mx - GRID_OFFSET_X) // self.tile_size
                    gy = (my - GRID_OFFSET_Y) // self.tile_size
                    
                    clicked_block = None
                    if self.grid_manager.is_valid_pos(gx, gy):
                        clicked_block = self.grid_manager.get_block_at(gx, gy)
                    
                    if clicked_block:
                        # Start Dragging
                        if self.selected_block:
                            self.selected_block.deselect()
                        self.selected_block = clicked_block
                        self.selected_block.select()
                        self.selected_block.dragging = True
                        self.selected_block.drag_offset_x = mx - self.selected_block.rect.x
                        self.selected_block.drag_offset_y = my - self.selected_block.rect.y
                        
                    else:
                        # Clicked empty space or wall
                        if self.selected_block and not self.selected_block.dragging:
                            # Check if adjacent (Click to Move logic)
                            self.target_x = self.offset_x + self.grid_x * self.tile_size
                            self.target_y = self.offset_y + self.grid_y * self.tile_size                           
                            dx = gx - self.selected_block.grid_x
                            dy = gy - self.selected_block.grid_y
                            
                            if abs(dx) + abs(dy) == 1: # Adjacent
                                if self.grid_manager.try_move(self.selected_block, dx, dy):
                                    self.selected_block.move(dx, dy)
                                    self.audio_manager.play_move()
                                    self.move_count += 1
                                    self.check_collection(self.selected_block)
                                    self.check_pending_spawns()
                                    self.check_deadlock()
                            else:
                                self.selected_block.deselect()
                                self.selected_block = None

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.selected_block and self.selected_block.dragging:
                        self.selected_block.dragging = False
                        
                        center_x = self.selected_block.rect.centerx
                        center_y = self.selected_block.rect.centery
                        
                        drop_gx = (center_x - GRID_OFFSET_X) // self.tile_size
                        drop_gy = (center_y - GRID_OFFSET_Y) // self.tile_size
                        
                        dx = drop_gx - self.selected_block.grid_x
                        dy = drop_gy - self.selected_block.grid_y
                        
                        # Allow ANY valid move (not just adjacent)
                        if dx != 0 or dy != 0:
                             if self.grid_manager.try_move(self.selected_block, dx, dy):
                                self.selected_block.move(dx, dy)
                                self.audio_manager.play_move()
                                self.move_count += 1
                                self.check_collection(self.selected_block)
                                self.check_pending_spawns()
                                self.check_deadlock()
                                moved = True
                        
                        # If not moved, block slides back in update()

            elif event.type == pygame.MOUSEMOTION:
                if self.selected_block and self.selected_block.dragging:
                    mx, my = pygame.mouse.get_pos()
                    self.selected_block.rect.x = mx - self.selected_block.drag_offset_x
                    self.selected_block.rect.y = my - self.selected_block.drag_offset_y
                    
                    # Calculate preview position for ghost
                    center_x = self.selected_block.rect.centerx
                    center_y = self.selected_block.rect.centery
                    preview_gx = (center_x - GRID_OFFSET_X) // self.tile_size
                    preview_gy = (center_y - GRID_OFFSET_Y) // self.tile_size
                    
                    # Check if preview position is valid
                    dx_preview = preview_gx - self.selected_block.grid_x
                    dy_preview = preview_gy - self.selected_block.grid_y
                    
                    self.preview_valid = False
                    self.preview_pos = None
                    if dx_preview != 0 or dy_preview != 0:
                        if self.grid_manager.try_move(self.selected_block, dx_preview, dy_preview):
                            self.preview_valid = True
                            self.preview_pos = (preview_gx, preview_gy)
                        else:
                            self.preview_valid = False
                            self.preview_pos = (preview_gx, preview_gy)
                            
            elif event.type == pygame.KEYDOWN:
                if self.selected_block:
                    dx, dy = 0, 0
                    if event.key == pygame.K_LEFT: dx = -1
                    elif event.key == pygame.K_RIGHT: dx = 1
                    elif event.key == pygame.K_UP: dy = -1
                    elif event.key == pygame.K_DOWN: dy = 1
                    
                    if dx != 0 or dy != 0:
                        if self.grid_manager.try_move(self.selected_block, dx, dy):
                            self.selected_block.move(dx, dy)
                            self.audio_manager.play_move()
                            self.move_count += 1
                            self.check_collection(self.selected_block)
                            self.check_pending_spawns()
                            self.check_deadlock()

    def check_deadlock(self):
        """Check if player is stuck (no valid moves) and trigger game over"""
        if not self.level_complete and not self.is_deadlocked:
            if len(self.block_sprites) > 0 and not self.grid_manager.has_valid_moves():
                self.is_deadlocked = True
                self.audio_manager.play_fail()
                # Could add a visual indicator or message here

    def check_collection(self, block):
        # Check for overlap with coins on ANY cell of the block
        for coin in list(self.coin_sprites):  # Use list() to avoid modification during iteration
            for cell_x, cell_y in block.get_occupied_cells():
                if cell_x == coin.grid_x and cell_y == coin.grid_y:
                    # Check color match (using string keys from data)
                    if block.block_data['color'] == coin.coin_data['color']:
                        # Collect!
                        coin.kill() # Remove from all groups
                        block.counter -= 1
                        block.update_appearance()
                        block.update_appearance()
                        self.audio_manager.play_collect()
                        
                        # Track collection for UI
                        if not hasattr(self, 'coins_collected_per_color'):
                            self.coins_collected_per_color = {}
                        self.coins_collected_per_color[block.block_data['color']] = \
                            self.coins_collected_per_color.get(block.block_data['color'], 0) + 1
                        
                        if block.counter <= 0:
                            block.kill()
                            self.selected_block = None
                            # Remove from grid manager blocks list
                            if block in self.grid_manager.blocks:
                                self.grid_manager.blocks.remove(block)
                        break  # Only collect once per coin
                            
        self.check_win_condition()

    def check_win_condition(self):
        # Check if all blocks are gone AND all coin queues are empty
        queues_empty = all(not q['items'] for q in self.coin_queues)
        
        if len(self.block_sprites) == 0 and len(self.coin_sprites) == 0 and queues_empty:
            self.level_complete = True
            self.level_complete_time = pygame.time.get_ticks()
            
            # Calculate stars based on move count (per GDD: sempre almeno 1 stella se completato)
            thresholds = self.level_data.get('stars_thresholds', [999, 999, 999])
            # GDD: stars = 3 if moves <= threshold[0], 2 if <= threshold[1], 1 otherwise
            if len(thresholds) >= 3:
                if self.move_count <= thresholds[0]:
                    self.stars_earned = 3
                elif self.move_count <= thresholds[1]:
                    self.stars_earned = 2
                else:
                    self.stars_earned = 1  # Always at least 1 star for completion
            else:
                self.stars_earned = 1
            
            # Save progress
            elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
            self.save_system.complete_level(
                self.level_data['id'],
                self.stars_earned,
                self.move_count,
                elapsed_time
            )
            
            # Calculate gold earned
            self.gold_earned_this_level = 10 + (self.stars_earned * 5)
            
            self.audio_manager.play_win()

    def update(self, dt):
        # Update UI animations (needed for timer pulse)
        self.ui.update(dt)
        
        if self.state == self.STATE_PLAY:
            self.all_sprites.update()
            
            # Update Timer
            elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
            time_remaining = max(0, self.time_limit - elapsed_time)
            
            # Check Timer States
            if time_remaining <= 0:
                if not self.level_complete:
                    self.handle_level_fail("Time's Up!")
            elif time_remaining <= self.time_limit * 0.2: # 20%
                self.timer_state = "CRITICAL"
                # TODO: Play warning sound if not playing
            elif time_remaining <= self.time_limit * 0.5: # 50%
                self.timer_state = "WARNING"
            else:
                self.timer_state = "NORMAL"
            
            # Check if level is complete and transition to victory state
            if self.level_complete and self.state == self.STATE_PLAY:
                self.state = self.STATE_VICTORY

    def handle_level_fail(self, reason):
        self.state = self.STATE_DEFEAT
        self.audio_manager.play_fail()
        self.lives = max(0, self.lives - 1)
        # Save lives update (if save system supports it)
        # self.save_system.update_lives(self.lives)

    def draw(self, screen):
        if self.state == self.STATE_MENU:
            self.ui.draw_menu(screen)
        elif self.state == self.STATE_VICTORY:
            elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
            time_remaining = max(0, self.time_limit - elapsed_time)
            self.ui.draw_victory(screen, stars=self.stars_earned, moves=self.move_count, 
                               time_remaining=time_remaining, gold_earned=self.gold_earned_this_level)
        elif self.state == self.STATE_DEFEAT:
            self.ui.draw_defeat(screen, reason="Tempo Scaduto", lives_remaining=self.lives)
        elif self.state == self.STATE_PLAY:
            screen.fill(BG_COLOR)
            self.draw_grid(screen)
            
            # Draw preview ghost if dragging
            if self.selected_block and self.selected_block.dragging and self.preview_pos:
                self.draw_preview_ghost(screen, self.selected_block, self.preview_pos, self.preview_valid)
            
            self.all_sprites.draw(screen)
            
            elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
            time_remaining = max(0, self.time_limit - elapsed_time)
            
            # Collect objective data - Calculate required coins from blocks
            self.objectives = {}
            
            # Initialize coins_collected_per_color if not exists
            if not hasattr(self, 'coins_collected_per_color'):
                self.coins_collected_per_color = {}
            
            # Calculate required coins per color from block counters
            # Per GDD: Total coins of color C = Sum of counters of blocks of color C
            coins_required_per_color = {}
            for block in self.grid_manager.blocks:
                color = block.block_data['color']
                coins_required_per_color[color] = coins_required_per_color.get(color, 0) + block.counter
            
            # Also count coins still in queues (they will be required)
            for queue in self.coin_queues:
                for color in queue['items']:
                    coins_required_per_color[color] = coins_required_per_color.get(color, 0) + 1
            
            # Build objectives dict
            for color in COLORS:
                required = coins_required_per_color.get(color, 0)
                collected = self.coins_collected_per_color.get(color, 0)
                
                # Only show colors that have requirements
                if required > 0:
                    self.objectives[color] = required # Store just required count for now, or dict?
                    # UI expects: for i, (color, required) in enumerate(game_state.level_data['objectives'].items()):
                    # Wait, UI expects game_state.level_data['objectives'] to be a dict of {color: required}
                    # But previously it was passed as 'objectives' arg which was {color: {'collected': c, 'required': r}}
                    
                    # Let's check UI code again.
                    # UI code: for i, (color, required) in enumerate(game_state.level_data['objectives'].items()):
                    # collected = game_state.collected_counts.get(color, 0)
                    
                    # So UI expects game_state.level_data['objectives'] to be {color: required_count}
                    # And it gets collected from game_state.collected_counts.
                    
                    # So here in game.py, I should probably update self.level_data['objectives']?
                    # But level_data is loaded from JSON, modifying it might persist or be wrong if we reload.
                    # Better to use self.objectives and update UI to use self.objectives.
                    
                    self.objectives[color] = required
            
            self.ui.draw(screen, self)
            
            # Victory message is now handled by STATE_VICTORY, so we don't draw it here
            # The level_complete flag triggers state change in update()
            if self.is_deadlocked:
                self.ui.draw_message(screen, "No valid moves! Press R to restart.")
                
            # Draw Tutorial Text if present
            if self.state == self.STATE_PLAY and self.level_data.get('tutorial_text'):
                self.ui.draw_tutorial(screen, self.level_data['tutorial_text'])

    def draw_preview_ghost(self, screen, block, preview_pos, is_valid):
        """Draw ghost preview of block at preview position"""
        preview_gx, preview_gy = preview_pos
        
        # Color: green if valid, red if invalid
        ghost_color = BLOCK_COLORS['GREEN']['main'] if is_valid else BLOCK_COLORS['RED']['main']
        alpha = 102  # 40% opacity (0.4 * 255)
        
        # Draw each cell of the block shape at preview position
        gap = 4
        cell_size = self.tile_size - gap
        offset = gap // 2
        
        for dx, dy in block.shape_cells:
            cell_x = GRID_OFFSET_X + (preview_gx + dx) * self.tile_size + offset
            cell_y = GRID_OFFSET_Y + (preview_gy + dy) * self.tile_size + offset
            
            # Create semi-transparent surface
            ghost_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
            pygame.draw.rect(ghost_surface, (*ghost_color, alpha), (0, 0, cell_size, cell_size), 
                           width=3, border_radius=8)
            screen.blit(ghost_surface, (cell_x, cell_y))
    
    def draw_grid(self, screen):
        # Draw grid based on actual level dimensions
        cols = self.level_data['grid_cols']
        rows = self.level_data['grid_rows']
        
        grid_width = cols * self.tile_size
        grid_height = rows * self.tile_size
        grid_rect = pygame.Rect(GRID_OFFSET_X, GRID_OFFSET_Y, grid_width, grid_height)
        
        # Mockup Style: "Tray"
        # 1. Deep Shadow (Bottom/Right)
        # 2. Main Tray Body (Light Blue)
        # 3. Inner Border/Highlight
        
        # Tray Padding (The tray is slightly larger than the grid)
        tray_padding = 10
        tray_rect = grid_rect.inflate(tray_padding * 2, tray_padding * 2)
        
        # 1. Deep Shadow (3D effect downwards)
        shadow_depth = 15
        shadow_rect = tray_rect.copy()
        shadow_rect.height += shadow_depth
        pygame.draw.rect(screen, TRAY_SHADOW, shadow_rect, border_radius=15)
        
        # 2. Main Tray Body
        pygame.draw.rect(screen, TRAY_BG, tray_rect, border_radius=15)
        
        # 3. Border (Slightly darker blue)
        pygame.draw.rect(screen, TRAY_BORDER, tray_rect, 4, border_radius=15)
        
        # Draw static elements (Walls, Voids, Empty Cells)
        
        # Draw static elements (Walls, Voids, Empty Cells)
        for row in range(rows):
            for col in range(cols):
                x = GRID_OFFSET_X + col * self.tile_size
                y = GRID_OFFSET_Y + row * self.tile_size
                
                cell_value = self.level_data['layout'][row][col]
                rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                
                # Shrink rect slightly for "gap-1" effect (4px gap)
                gap = 2
                cell_rect = rect.inflate(-gap*2, -gap*2)
                
                if cell_value == 1:  # Wall
                    # Walls should look like part of the tray structure
                    # Use Tray Border color
                    pygame.draw.rect(screen, TRAY_BORDER, cell_rect, border_radius=8)
                    
                elif cell_value == 2:  # Void
                    # Transparent/Background
                    pass
                else:  # Empty Cell
                    # Light Gray cells
                    pygame.draw.rect(screen, GRID_CELL_BG, cell_rect, border_radius=4)
                    # Optional: faint border
                    # pygame.draw.rect(screen, GRID_LINE_COLOR, cell_rect, 1, border_radius=4)
