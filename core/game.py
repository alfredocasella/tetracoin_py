import pygame
import sys
import math  # For spawn queue pulse animation
from core.settings import *
from core.grid_manager import GridManager

from core.sprites import BlockSprite, CoinSprite, PiggyBankSprite, ObstacleSprite
from ui.ui import UI
from core.audio_manager import AudioManager
from core.level_loader import LevelLoader
from core.save_system import SaveSystem
from src.tetracoin.spec import GridState, EntityType, ColorType, PhysicsEngine, Entity, Coin, PiggyBank, Obstacle, FixedBlock
from typing import Optional

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TetraCoin")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize UI with screen
        self.ui = UI(self.screen)
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
        
        # New Physics Engine State
        self.grid_state: GridState = None
        self.mode = "LEGACY" # "LEGACY" or "PHYSICS"
        
        # PHYSICS mode gameplay state
        self.selected_entity_id: Optional[str] = None  # ID of selected movable entity
        self.physics_move_count = 0  # Track moves in PHYSICS mode

    def _init_physics_level(self):
        """Initialize the game state from the new spec level data."""
        print("Initializing Physics Level...")
        rows = self.level_data['grid']['rows']
        cols = self.level_data['grid']['cols']
        
        # Create GridState
        self.grid_state = GridState(rows=rows, cols=cols)
        
        # Convert entities JSON to Dataclasses
        for e_data in self.level_data['entities']:
            etype = EntityType(e_data['type'])
            color = ColorType(e_data['color'])
            
            if etype == EntityType.COIN:
                entity = Coin(id=e_data['id'], row=e_data['row'], col=e_data['col'], color=color)
            elif etype == EntityType.PIGGYBANK:
                entity = PiggyBank(id=e_data['id'], row=e_data['row'], col=e_data['col'], color=color)
                entity.capacity = e_data.get('capacity', 5)
                entity.current_count = e_data.get('current_count', 0)
            elif etype == EntityType.OBSTACLE:
                entity = Obstacle(id=e_data['id'], row=e_data['row'], col=e_data['col'], color=color)
            elif etype == EntityType.FIXED_BLOCK:
                entity = FixedBlock(id=e_data['id'], row=e_data['row'], col=e_data['col'], color=color)
            
            self.grid_state.entities.append(entity)
            
        # Init visual environment
        max_grid_width = SCREEN_WIDTH - 20
        max_grid_height = GRID_AREA_HEIGHT - 20
        tile_size_w = max_grid_width // cols
        tile_size_h = max_grid_height // rows
        self.tile_size = min(TILE_SIZE, tile_size_w, tile_size_h)
        
        grid_pixel_width = cols * self.tile_size
        grid_pixel_height = rows * self.tile_size
        global GRID_OFFSET_X, GRID_OFFSET_Y
        GRID_OFFSET_X = (SCREEN_WIDTH - grid_pixel_width) // 2
        GRID_OFFSET_Y = TOP_HUD_HEIGHT + (GRID_AREA_HEIGHT - grid_pixel_height) // 2
        
        # Create Sprites
        self.all_sprites = pygame.sprite.Group()
        self.coin_sprites = pygame.sprite.Group()
        self.block_sprites = pygame.sprite.Group() # Reuse block sprites for non-coins?
        
        self.entity_sprite_map = {} # Map entity_id -> sprite
        self._sync_sprites_to_state(rebuild=True)
        
    def _sync_sprites_to_state(self, rebuild=False):
        """Synchronize Pygame sprites with the logical GridState."""
        if rebuild:
            self.all_sprites.empty()
            self.coin_sprites.empty()
            self.block_sprites.empty()
            self.entity_sprite_map.clear()
            
            for entity in self.grid_state.entities:
                if entity.is_collected:
                    continue
                    
                # Setup data dict expected by sprites
                # We reuse existing Sprite classes for now, or adapt them.
                # CoinSprite expects {'pos': (col, row), 'color': ...}
                pos = (entity.col, entity.row)
                
                if entity.type == EntityType.COIN:
                    data = {'pos': pos, 'color': entity.color.value}
                    sprite = CoinSprite(data, [self.all_sprites, self.coin_sprites],
                                      grid_offsets=(GRID_OFFSET_X, GRID_OFFSET_Y), tile_size=self.tile_size)
                    self.entity_sprite_map[entity.id] = sprite
                    
                elif entity.type == EntityType.PIGGYBANK:
                    data = {
                        'pos': pos,
                        'color': entity.color.value,
                        'current': entity.current_count,
                        'capacity': entity.capacity
                    }
                    sprite = PiggyBankSprite(data, [self.all_sprites, self.block_sprites],
                                       grid_offsets=(GRID_OFFSET_X, GRID_OFFSET_Y), tile_size=self.tile_size)
                    self.entity_sprite_map[entity.id] = sprite
                    
                elif entity.type == EntityType.OBSTACLE:
                    data = {'pos': pos}
                    sprite = ObstacleSprite(data, [self.all_sprites, self.block_sprites],
                                      grid_offsets=(GRID_OFFSET_X, GRID_OFFSET_Y), tile_size=self.tile_size)
                    self.entity_sprite_map[entity.id] = sprite
        else:
            # Positional update only
            for entity in self.grid_state.entities:
                if entity.is_collected:
                    if entity.id in self.entity_sprite_map:
                        self.entity_sprite_map[entity.id].kill()
                        del self.entity_sprite_map[entity.id]
                    continue
                    
                if entity.id in self.entity_sprite_map:
                    sprite = self.entity_sprite_map[entity.id]
                    # Direct position update (bypass animation for now)
                    sprite.grid_x = entity.col
                    sprite.grid_y = entity.row
                    # Manually update rect if we bypass Sprite.update logic
                    sprite.rect.x = GRID_OFFSET_X + entity.col * self.tile_size
                    sprite.rect.y = GRID_OFFSET_Y + entity.row * self.tile_size - (15 if entity.type == EntityType.COIN else 0)

    def _init_legacy_level(self):
        """Initialize the game state from legacy level format."""
        print("Initializing Legacy Level...")
        
        self.grid_manager = GridManager(self.level_data)
        self.grid_manager._game_ref = self  # Store reference for coin collision check
        
        # Calculate dynamic grid offset to center it in the GRID_AREA
        max_grid_width = SCREEN_WIDTH - 20
        max_grid_height = GRID_AREA_HEIGHT - 20
        
        tile_size_w = max_grid_width // self.level_data['grid_cols']
        tile_size_h = max_grid_height // self.level_data['grid_rows']
        
        self.tile_size = min(TILE_SIZE, tile_size_w, tile_size_h)
        
        grid_pixel_width = self.level_data['grid_cols'] * self.tile_size
        grid_pixel_height = self.level_data['grid_rows'] * self.tile_size
        
        global GRID_OFFSET_X, GRID_OFFSET_Y
        GRID_OFFSET_X = (SCREEN_WIDTH - grid_pixel_width) // 2
        GRID_OFFSET_Y = TOP_HUD_HEIGHT + (GRID_AREA_HEIGHT - grid_pixel_height) // 2
        
        # Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.block_sprites = pygame.sprite.Group()
        self.coin_sprites = pygame.sprite.Group()
        
        # Create Block Sprites
        for block_data in self.level_data['blocks']:
            block = BlockSprite(block_data, [self.all_sprites, self.block_sprites], 
                              grid_offsets=(GRID_OFFSET_X, GRID_OFFSET_Y), tile_size=self.tile_size)
            self.grid_manager.register_block(block)
            
        # Create Coin Sprites (DROP AWAY STYLE: Static + Queue spawning)
        self.coin_queues = []  # RESTORED: Essential for Drop Away spawning!
        coins_data = self.level_data.get('coins', {})
        
        if isinstance(coins_data, list):
            # Legacy format: list of coins (all static)
            for coin_data in coins_data:
                CoinSprite(coin_data, [self.all_sprites, self.coin_sprites],
                         grid_offsets=(GRID_OFFSET_X, GRID_OFFSET_Y), tile_size=self.tile_size)
        else:
            # New format: dict with 'static' and 'queues'
            # Static coins
            for coin_data in coins_data.get('static', []):
                CoinSprite(coin_data, [self.all_sprites, self.coin_sprites],
                         grid_offsets=(GRID_OFFSET_X, GRID_OFFSET_Y), tile_size=self.tile_size)
            
            # Queue spawning (DROP AWAY STYLE: continuous spawning from tube)
            queues_list = coins_data.get('queues', [])
            for queue_data in queues_list:
                self.coin_queues.append({
                    'pos': queue_data['pos'],
                    'items': list(queue_data['items'])
                })
                self.process_coin_queue(self.coin_queues[-1])
        

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
                # No fallback available, return to menu
                self.state = self.STATE_MENU
                return
        else:
            # JSON-only mode, no Python fallback
            self.state = self.STATE_MENU
            return
            
        # Auto-detect mode based on level format
        if 'grid' in self.level_data and 'entities' in self.level_data:
            # V2 format - use PHYSICS mode
            self.mode = "PHYSICS"
            self._init_physics_level()
        else:
            # Legacy format - use LEGACY mode
            self.mode = "LEGACY"
            self._init_legacy_level()
            
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
        
        # Timer and objectives
        # CRITICAL FIX: time_limit is in meta object, not root!
        self.time_limit = self.level_data.get('meta', {}).get('time_limit', 180)
        
        self.start_time = pygame.time.get_ticks()
        self.move_count = 0
        self.lives = 5 # Should load from save system
        self.timer_state = "NORMAL" # NORMAL, WARNING, CRITICAL

    # ========== DROP AWAY COIN SPAWNING SYSTEM ==========
    def process_coin_queue(self, queue):
        """Process coin queue spawning (DROP AWAY style: continuous from tube)"""
        if not queue['items']:
            return
            
        next_color = queue['items'][0]
        pos = queue['pos']
        
        block_at_pos = self.grid_manager.get_block_at(pos[0], pos[1])
        
        if block_at_pos:
            # SPAWN PARADOX: Block on spawn point
            if block_at_pos.block_data['color'] == next_color:
                # Same color: Instant Collect!
                queue['items'].pop(0)
                block_at_pos.counter -= 1
                block_at_pos.update_appearance()
                self.audio_manager.play_collect()
                
                if block_at_pos.counter <= 0:
                    block_at_pos.kill()
                    if self.selected_block == block_at_pos:
                        self.selected_block = None
                    if block_at_pos in self.grid_manager.blocks:
                        self.grid_manager.blocks.remove(block_at_pos)
                
                self.process_coin_queue(queue)
            # Different color: wait for block to move
        else:
            # Space free: Spawn coin
            color = queue['items'].pop(0)
            CoinSprite({'color': color, 'pos': pos}, [self.all_sprites, self.coin_sprites],
                     grid_offsets=(GRID_OFFSET_X, GRID_OFFSET_Y), tile_size=self.tile_size)

    def check_pending_spawns(self):
        """Check all queues for pending spawns (DROP AWAY style)"""
        for queue in self.coin_queues:
            if queue['items']:
                pos = queue['pos']
                coin_exists = any(coin.grid_x == pos[0] and coin.grid_y == pos[1] 
                                for coin in self.coin_sprites)
                
                if not coin_exists:
                    self.process_coin_queue(queue)
    # ========== END DROP AWAY COIN SPAWNING ==========

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
                        # No Python levels available
                        print(f"All levels completed!")
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
                if event.button == 1:  # Left click - handle both modes
                    if self.mode == "PHYSICS":
                        self._handle_physics_mouse_down(event)
                    elif self.mode == "LEGACY":
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
                                # Check if adjacent (Click to Move logic)                        
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
                    if self.mode == "PHYSICS":
                        self._handle_physics_mouse_up(event)
                    elif self.mode == "LEGACY":
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
                                    self.check_pending_spawns()  # RESTORED for Drop Away
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
                if self.mode == "PHYSICS" and self.selected_entity_id:
                    self._handle_physics_keyboard(event)
                elif self.selected_block and self.mode == "LEGACY":
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
                            self.check_pending_spawns()  # RESTORED for Drop Away
                            self.check_deadlock()

    # ========== PHYSICS MODE INPUT HANDLING ==========
    
    def _handle_physics_mouse_down(self, event):
        """Handle mouse down in PHYSICS mode - select movable entities."""
        mx, my = pygame.mouse.get_pos()
        gx = (mx - GRID_OFFSET_X) // self.tile_size
        gy = (my - GRID_OFFSET_Y) // self.tile_size
        
        # Find entity at clicked position
        clicked_entity = self._get_entity_at(gy, gx)  # Note: row, col
        
        if clicked_entity and self._is_movable(clicked_entity):
            # Select this entity
            self.selected_entity_id = clicked_entity.id
            print(f"Selected entity: {clicked_entity.id} ({clicked_entity.type})")
        else:
            # Deselect if clicking empty space
            if self.selected_entity_id:
                print(f"Deselected entity")
                self.selected_entity_id = None
    
    def _handle_physics_mouse_up(self, event):
        """Handle mouse up in PHYSICS mode."""
        # For now, we keep selection active until user clicks elsewhere or uses keyboard
        pass
    
    def _handle_physics_keyboard(self, event):
        """Handle keyboard input in PHYSICS mode - move selected entity."""
        if not self.selected_entity_id:
            return
            
        dx, dy = 0, 0
        if event.key == pygame.K_LEFT: dx = -1
        elif event.key == pygame.K_RIGHT: dx = 1
        elif event.key == pygame.K_UP: dy = -1
        elif event.key == pygame.K_DOWN: dy = 1
        elif event.key == pygame.K_ESCAPE:
            self.selected_entity_id = None
            print("Deselected entity")
            return
        
        if dx != 0 or dy != 0:
            self._move_entity_physics(self.selected_entity_id, dx, dy)
    
    def _get_entity_at(self, row: int, col: int) -> Optional[Entity]:
        """Get entity at grid position (row, col)."""
        if not self.grid_state:
            return None
        for entity in self.grid_state.entities:
            if not entity.is_collected and entity.row == row and entity.col == col:
                return entity
        return None
    
    def _is_movable(self, entity: Entity) -> bool:
        """Check if entity type is movable by player."""
        movable_types = {EntityType.OBSTACLE, EntityType.SUPPORT, EntityType.DEFLECTOR}
        return entity.type in movable_types
    
    def _move_entity_physics(self, entity_id: str, dx: int, dy: int):
        """Move an entity in PHYSICS mode and trigger physics update."""
        if not self.grid_state:
            return
            
        # Find entity
        entity = next((e for e in self.grid_state.entities if e.id == entity_id), None)
        if not entity:
            return
        
        new_row = entity.row + dy
        new_col = entity.col + dx
        
        # Check bounds
        if not (0 <= new_row < self.grid_state.rows and 0 <= new_col < self.grid_state.cols):
            print(f"Move out of bounds")
            return
        
        # Check collision with other entities
        if self._get_entity_at(new_row, new_col):
            print(f"Position occupied")
            return
        
        # Apply move
        entity.row = new_row
        entity.col = new_col
        self.physics_move_count += 1
        self.audio_manager.play_move()
        print(f"Moved {entity.id} to ({new_row}, {new_col})")
        
        # Physics will update in next update() cycle
    
    def _check_physics_win_condition(self):
        """Check if all coins are collected in PHYSICS mode."""
        if not self.grid_state:
            return
        
        # Count uncollected coins
        uncollected_coins = sum(1 for e in self.grid_state.entities 
                               if e.type == EntityType.COIN and not e.is_collected)
        
        if uncollected_coins == 0 and not self.level_complete:
            self.level_complete = True
            self.level_complete_time = pygame.time.get_ticks()
            
            # Calculate stars based on move count
            # For PHYSICS mode, use physics_move_count
            move_count = self.physics_move_count
            
            # Simple star calculation (can be refined)
            if move_count <= 10:
                self.stars_earned = 3
            elif move_count <= 20:
                self.stars_earned = 2
            else:
                self.stars_earned = 1
            
            # Save progress
            elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
            level_id = self.level_data.get('id', f'level_{self.current_level_index + 1:03d}')
            self.save_system.complete_level(
                level_id,
                self.stars_earned,
                move_count,
                elapsed_time
            )
            
            # Calculate gold earned
            self.gold_earned_this_level = 10 + (self.stars_earned * 5)
            
            self.audio_manager.play_win()
            print(f"Level Complete! Stars: {self.stars_earned}, Moves: {move_count}")
    
    # ========== END PHYSICS MODE INPUT HANDLING ==========

    def check_deadlock(self):
        """Check if player is stuck (no valid moves) and trigger game over"""
        if self.mode == "LEGACY" and not self.level_complete and not self.is_deadlocked:
            if len(self.block_sprites) > 0 and not self.grid_manager.has_valid_moves():
                self.is_deadlocked = True
                self.audio_manager.play_fail()
                # Could add a visual indicator or message here

    def check_collection(self, block):
        """Check for coin collection and remove block when empty (Drop Away style)"""
        for coin in list(self.coin_sprites):
            for cell_x, cell_y in block.get_occupied_cells():
                if cell_x == coin.grid_x and cell_y == coin.grid_y:
                    if block.block_data['color'] == coin.coin_data['color']:
                        # Collect coin
                        coin.kill()
                        block.counter -= 1
                        block.update_appearance()
                        self.audio_manager.play_collect()
                        
                        # Track collection
                        if not hasattr(self, 'coins_collected_per_color'):
                            self.coins_collected_per_color = {}
                        self.coins_collected_per_color[block.block_data['color']] = \
                            self.coins_collected_per_color.get(block.block_data['color'], 0) + 1
                        
                        # DROP AWAY: Block disappears when counter reaches 0
                        if block.counter <= 0:
                            block.kill()  # Remove from all sprite groups
                            if self.selected_block == block:
                                self.selected_block = None
                            if block in self.grid_manager.blocks:
                                self.grid_manager.blocks.remove(block)
                        break  # Only collect once per coin
                            
        self.check_win_condition()

    def check_win_condition(self):
        """
        DROP AWAY STYLE WIN CONDITION:
        Level is complete when ALL BLOCKS have disappeared (been removed from game)
        Blocks disappear when their counter reaches 0
        """
        if self.mode != "LEGACY":
            return
        
        # Win condition: NO blocks remaining on screen
        if len(self.block_sprites) == 0 and not self.level_complete:
            self.level_complete = True
            self.level_complete_time = pygame.time.get_ticks()
            
            # Calculate stars based on move count
            thresholds = self.level_data.get('stars_thresholds', [999, 999, 999])
            if len(thresholds) >= 3:
                if self.move_count <= thresholds[0]:
                    self.stars_earned = 3
                elif self.move_count <= thresholds[1]:
                    self.stars_earned = 2
                else:
                    self.stars_earned = 1
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
        
        if self.mode == "PHYSICS" and self.state == self.STATE_PLAY:
            # ========== PHYSICS MODE UPDATE FLOW ==========
            # 1. Input is handled in handle_input() (already integrated)
            # 2. Gameplay logic (move validation done in _move_entity_physics)
            # 3. Physics Step
            if self.grid_state:
                self.grid_state, events = PhysicsEngine.update(self.grid_state)
                
                # 4. Handle Physics Events (coin collection, etc.)
                for event in events:
                    if event.startswith("COLLECT_"):
                        color = event.split("_")[1]
                        self.audio_manager.play_collect()
                        # Update stats if needed
                
                # 5. Sync Sprites with State
                self._sync_sprites_to_state()
                
                # 6. Check Win Condition (all coins collected)
                self._check_physics_win_condition()
            
            # 7. Update Timer
            elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
            time_remaining = max(0, self.time_limit - elapsed_time)
            
            if time_remaining <= 0 and not self.level_complete:
                self.handle_level_fail("Time's Up!")
            elif time_remaining <= self.time_limit * 0.2:
                self.timer_state = "CRITICAL"
            elif time_remaining <= self.time_limit * 0.5:
                self.timer_state = "WARNING"
            else:
                self.timer_state = "NORMAL"
            
            # 8. Sprite updates (animations, etc.)
            self.all_sprites.update()
            
            # 9. Check if level is complete and transition to victory
            if self.level_complete and self.state == self.STATE_PLAY:
                self.state = self.STATE_VICTORY
            
            return
            # ========== END PHYSICS MODE UPDATE FLOW ==========

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
            if self.mode == "PHYSICS":
                screen.fill(BG_COLOR)
                self.draw_grid(screen)
                self.all_sprites.draw(screen)
                # self.ui.draw(screen, self) # Draw UI even in physics mode? Yes mostly.
                # But ui.draw relies on game stats.
                # Let's bypass UI call for now in PHYSICS mode if it causes issues, or adapt UI.
                return

            screen.fill(BG_COLOR)
            self.draw_grid(screen)
            self.draw_grid_cells(screen)  # Draw grid cells
            
            # Draw spawn queues (Drop Away style)
            self.draw_spawn_queues(screen)
            
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
            if self.mode == "LEGACY":
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
            
            if self.mode == "PHYSICS":
                # In physics mode, grid is drawn based on grid_state
                # We can reuse draw_grid if we adapt it or just rely on sprites and background
                self.draw_grid(screen) # Needs adaptation for dynamic size?
                self.all_sprites.draw(screen)
                return

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
        if self.mode == "PHYSICS" and self.grid_state:
            cols = self.grid_state.cols
            rows = self.grid_state.rows
        else:
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
    
    def draw_spawn_queues(self, screen):
        """Draw spawn queue visualization (3D isometric DOOR - outside grid, 1 tile size)"""
        if not hasattr(self, 'coin_queues') or not self.coin_queues:
            return
        
        for queue in self.coin_queues:
            if not queue['items']:
                continue
                
            spawn_x, spawn_y = queue['pos']
            
            # Screen position of spawn cell
            screen_x = GRID_OFFSET_X + spawn_x * self.tile_size
            screen_y = GRID_OFFSET_Y + spawn_y * self.tile_size
            center_x = screen_x + self.tile_size // 2
            
            # Position door OUTSIDE and ABOVE the grid
            # Door is exactly 1 tile size in isometric view
            door_size = self.tile_size
            
            # Position door above the spawn cell, outside grid boundary
            door_center_x = center_x
            door_bottom_y = GRID_OFFSET_Y - 10  # Just above grid
            door_top_y = door_bottom_y - door_size
            
            # Isometric 3D door dimensions
            door_width = int(door_size * 0.6)  # Narrower for door look
            door_height = door_size
            door_x = door_center_x - door_width // 2
            door_y = door_top_y
            
            # 3D Isometric colors
            door_front = (160, 110, 80)   # Light brown (front)
            door_side = (120, 80, 60)     # Dark brown (side)
            door_edge = (80, 50, 30)      # Very dark (edges)
            window_color = (180, 200, 220)  # Light blue
            
            # Isometric depth
            depth = int(door_size * 0.15)
            
            # 1. Draw LEFT SIDE (isometric 3D depth)
            left_points = [
                (door_x, door_y),
                (door_x - depth, door_y - depth // 2),
                (door_x - depth, door_y + door_height - depth // 2),
                (door_x, door_y + door_height)
            ]
            pygame.draw.polygon(screen, door_side, left_points)
            pygame.draw.polygon(screen, door_edge, left_points, 1)
            
            # 2. Draw TOP (isometric 3D depth)
            top_points = [
                (door_x, door_y),
                (door_x - depth, door_y - depth // 2),
                (door_x + door_width - depth, door_y - depth // 2),
                (door_x + door_width, door_y)
            ]
            pygame.draw.polygon(screen, door_side, top_points)
            pygame.draw.polygon(screen, door_edge, top_points, 1)
            
            # 3. Draw FRONT FACE
            door_rect = pygame.Rect(door_x, door_y, door_width, door_height)
            pygame.draw.rect(screen, door_front, door_rect, border_radius=4)
            pygame.draw.rect(screen, door_edge, door_rect, width=2, border_radius=4)
            
            # 4. Draw window (centered, showing coins)
            window_size = int(door_width * 0.65)
            window_x = door_x + (door_width - window_size) // 2
            window_y = door_y + int(door_height * 0.3)
            window_rect = pygame.Rect(window_x, window_y, window_size, window_size)
            pygame.draw.rect(screen, window_color, window_rect, border_radius=3)
            pygame.draw.rect(screen, door_edge, window_rect, width=2, border_radius=3)
            
            # 5. Draw next 3 coins in window (stacked vertically)
            coins_to_show = min(3, len(queue['items']))
            if coins_to_show > 0:
                coin_size = int(window_size * 0.28)
                for i in range(coins_to_show):
                    color_key = queue['items'][i]
                    colors = COIN_COLORS.get(color_key, COIN_COLORS['YELLOW'])
                    
                    coin_cx = window_rect.centerx
                    coin_cy = window_rect.y + 8 + (i * (coin_size + 3))
                    
                    # Tiny coin circle
                    pygame.draw.circle(screen, colors['fill'], (coin_cx, coin_cy), coin_size // 2)
                    pygame.draw.circle(screen, colors['border'], (coin_cx, coin_cy), coin_size // 2, 1)
            
            # 6. Door handle (3D, right side)
            handle_x = door_x + door_width - 10
            handle_y = door_y + door_height // 2
            pygame.draw.circle(screen, (200, 180, 100), (handle_x, handle_y), 4)
            pygame.draw.circle(screen, door_edge, (handle_x, handle_y), 4, 1)
            # 3D depth
            pygame.draw.circle(screen, (150, 130, 70), (handle_x - 1, handle_y - 1), 3)
            
            # 7. Arrow from door to spawn cell
            arrow_color = (255, 200, 0)
            # Arrow starts at bottom of door
            arrow_start_y = door_bottom_y + 5
            arrow_end_y = screen_y - 5
            
            # Vertical line
            pygame.draw.line(screen, arrow_color, 
                           (center_x, arrow_start_y), 
                           (center_x, arrow_end_y), 3)
            
            # Arrow head pointing down
            arrow_points = [
                (center_x, arrow_end_y + 8),
                (center_x - 6, arrow_end_y),
                (center_x + 6, arrow_end_y)
            ]
            pygame.draw.polygon(screen, arrow_color, arrow_points)
            pygame.draw.polygon(screen, door_edge, arrow_points, 1)
            
            # 8. Pulsing spawn indicator on spawn cell
            pulse = abs(math.sin(pygame.time.get_ticks() / 500)) * 0.3 + 0.7
            indicator_color = (255, 200, 0, int(180 * pulse))
            pygame.draw.circle(screen, indicator_color, 
                             (center_x, screen_y + self.tile_size // 2), 
                             int(self.tile_size * 0.25 * pulse), 2)
    
    def draw_grid_cells(self, screen):
        """Draw grid cells (was accidentally removed from draw_grid)"""
        if not hasattr(self, 'level_data'):
            return
            
        rows = self.level_data.get('grid_rows', 8)
        cols = self.level_data.get('grid_cols', 6)
        
        # Drop Away style colors
        CELL_BASE_COLOR = (200, 230, 250)  # Lighter blue for cells
        CELL_BORDER_COLOR = (140, 180, 210)  # Darker blue for borders
        
        # Draw individual cells with 3D effect
        for row in range(rows):
            for col in range(cols):
                x = GRID_OFFSET_X + col * self.tile_size
                y = GRID_OFFSET_Y + row * self.tile_size
                
                # Cell with gradient (lighter at top, darker at bottom)
                cell_rect = pygame.Rect(x + 2, y + 2, self.tile_size - 4, self.tile_size - 4)
                
                # Draw cell base
                pygame.draw.rect(screen, CELL_BASE_COLOR, cell_rect, border_radius=5)
                
                # Draw border for 3D effect
                pygame.draw.rect(screen, CELL_BORDER_COLOR, cell_rect, width=2, border_radius=5)
                
                # Add highlight on top edge for 3D depth
                highlight_rect = pygame.Rect(x + 4, y + 4, self.tile_size - 8, 3)
                pygame.draw.rect(screen, (255, 255, 255, 80), highlight_rect, border_radius=2)
        
        if self.mode == "PHYSICS":
            return # Entities are drawn by sprites
            
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
