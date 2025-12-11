import pygame
import math
from core.settings import *

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        
        # Backward compatibility with old UI
        self.font_large = self.large_font
        self.font_medium = self.font
        self.font_small = self.small_font
        self.font_tiny = pygame.font.Font(None, 18)
        
        # DROP AWAY STYLE HUD COLORS
        self.level_badge_color = (138, 43, 226)  # Purple
        self.level_badge_border = (98, 0, 234)   # Darker purple
        self.timer_bg_color = (138, 43, 226)     # Purple
        self.timer_bar_green = (76, 175, 80)     # Green
        self.timer_bar_yellow = (255, 193, 7)    # Yellow
        self.timer_bar_red = (244, 67, 54)       # Red
        self.restart_button_color = (150, 150, 150)  # Gray
        
        # Animation state
        self.pulse_time = 0
        self.timer_pulse_time = 0
        
    def update(self, dt):
        """Update UI animations"""
        self.pulse_time += dt
        # Backward compatibility
        self.timer_pulse_time = self.pulse_time * 10
        
    def draw(self, screen, game_state):
        # 1. Draw Top HUD
        self.draw_top_hud(screen, game_state)
        
        # 2. Draw Grid Area Background (Optional, helps visualize layout)
        # grid_area_rect = pygame.Rect(0, TOP_HUD_HEIGHT, SCREEN_WIDTH, GRID_AREA_HEIGHT)
        # pygame.draw.rect(screen, BG_COLOR, grid_area_rect)
        
        # 3. Draw Objective Panel
        self.draw_objectives_panel(screen, game_state)
        
        # 4. Draw Bottom Bar
        self.draw_bottom_bar(screen, game_state)

    def draw_top_hud(self, screen, level_id, time_remaining, lives, gold, timer_state):
        # Background (Transparent/White)
        hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, TOP_HUD_HEIGHT)
        pygame.draw.rect(screen, BG_COLOR, hud_rect)
        
        # Level Info (Top Left)
        # Prototype: Teal rounded square with World number, Text "Mondo X - Livello Y"
        # We'll simplify to just "Level X" for now but use the style.
        
        # Teal Badge (32x32px per GDD)
        badge_size = 32
        badge_rect = pygame.Rect(20, 20, badge_size, badge_size)
        pygame.draw.rect(screen, COLOR_PRIMARY_TEAL, badge_rect, border_radius=8)
        
        # World Num (Hardcoded 1)
        world_text = self.font_tiny.render("1", True, COLOR_WHITE)
        world_rect = world_text.get_rect(center=badge_rect.center)
        screen.blit(world_text, world_rect)
        
        # Level Text (Bold, 32px per GDD) - Truncate if too long
        level_text_str = f"Mondo 1 - Livello {level_id}"
        level_text = self.font_medium.render(level_text_str, True, TEXT_COLOR)
        # Limit width to avoid overflow - ensure it doesn't overlap with timer
        max_text_width = SCREEN_WIDTH // 2 - badge_rect.right - 30  # Leave space for timer
        level_text_x = badge_rect.right + 10
        if level_text.get_width() > max_text_width:
            # Use smaller font if needed
            level_text = self.font_small.render(level_text_str, True, TEXT_COLOR)
        # Ensure text doesn't overlap with timer pillola (which starts around SCREEN_WIDTH/2 - 140)
        if level_text_x + level_text.get_width() > SCREEN_WIDTH // 2 - 150:
            # Truncate text
            max_chars = int((SCREEN_WIDTH // 2 - 150 - level_text_x) / 10)  # Approximate char width
            if max_chars > 0:
                level_text_str = f"Lv {level_id}"[:max_chars]
                level_text = self.font_small.render(level_text_str, True, TEXT_COLOR)
        screen.blit(level_text, (level_text_x, badge_rect.centery - level_text.get_height()//2))
        
        # Timer (Center) - Pillola style per GDD
        # Prototype: Pillola 260-320px larghezza, 56px altezza, bordo 2px, raggio 28px
        minutes = int(time_remaining) // 60
        seconds = int(time_remaining) % 60
        time_str = f"{minutes:02}:{seconds:02}"
        
        time_color = TEXT_COLOR
        if timer_state == "WARNING": 
            time_color = BLOCK_COLORS['ORANGE']['main']
            pulse_scale = 1.0
        elif timer_state == "CRITICAL": 
            time_color = BLOCK_COLORS['RED']['main']
            # Pulse animation for critical state
            pulse_scale = 1.0 + 0.1 * math.sin(self.timer_pulse_time * 10)
        else:
            pulse_scale = 1.0
    def draw_top_hud(self, screen, game_state):
        # 1. Purple Header Background
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, TOP_HUD_HEIGHT)
        pygame.draw.rect(screen, HEADER_BG, header_rect)
        
        # Bottom border of header (slightly lighter/darker purple)
        pygame.draw.line(screen, (123, 31, 162), (0, TOP_HUD_HEIGHT), (SCREEN_WIDTH, TOP_HUD_HEIGHT), 4)
        
        y_center = (TOP_HUD_HEIGHT + SAFE_AREA_TOP) // 2
        
        # 2. Level Badge (Top Left)
        # Yellow/Orange Rounded Rect
        badge_w = 100
        badge_h = 40
        badge_x = 20
        badge_y = y_center - badge_h // 2
        
        badge_rect = pygame.Rect(badge_x, badge_y, badge_w, badge_h)
        # Gradient effect (simulated with nested rects)
        pygame.draw.rect(screen, HEADER_BUTTON_BORDER, badge_rect, border_radius=10) # Border/Shadow
        inner_badge = badge_rect.inflate(-4, -4)
        pygame.draw.rect(screen, HEADER_BUTTON_YELLOW, inner_badge, border_radius=8) # Main fill
        
        # Text "Level X"
        level_text = self.font_small.render(f"Level {game_state.level_data['id']}", True, (255, 255, 255))
        # Drop shadow for text
        text_shadow = self.font_small.render(f"Level {game_state.level_data['id']}", True, (160, 0, 0))
        screen.blit(text_shadow, (badge_rect.centerx - level_text.get_width()//2 + 1, badge_rect.centery - level_text.get_height()//2 + 2))
        screen.blit(level_text, (badge_rect.centerx - level_text.get_width()//2, badge_rect.centery - level_text.get_height()//2))
        
        # 3. Timer Pill (Center)
        pill_w = 140
        pill_h = 40
        pill_x = (SCREEN_WIDTH - pill_w) // 2
        pill_y = y_center - pill_h // 2
        
        pill_rect = pygame.Rect(pill_x, pill_y, pill_w, pill_h)
        pygame.draw.rect(screen, HEADER_BUTTON_BORDER, pill_rect, border_radius=20) # Border
        inner_pill = pill_rect.inflate(-4, -4)
        pygame.draw.rect(screen, HEADER_TIMER_BG, inner_pill, border_radius=18) # Dark Brown Fill
        
        # Coin Icon on left of pill
        coin_radius = 14
        coin_center = (pill_x + 24, pill_y + pill_h // 2)
        pygame.draw.circle(screen, HEADER_BUTTON_YELLOW, coin_center, coin_radius)
        pygame.draw.circle(screen, HEADER_BUTTON_BORDER, coin_center, coin_radius, 2)
        # Inner detail
        pygame.draw.circle(screen, (255, 235, 59), coin_center, coin_radius - 4)
        
        # Timer Text
        time_left = 0
        if game_state.time_limit > 0:
            time_left = max(0, int(game_state.time_limit - (pygame.time.get_ticks() - game_state.start_time) / 1000))
        
        timer_str = f"{time_left // 60}:{time_left % 60:02d}"
        timer_text = self.font_medium.render(timer_str, True, (255, 255, 255))
        screen.blit(timer_text, (pill_x + 50, pill_y + 5))
        
        # 4. Back/Pause Button (Top Right)
        btn_size = 44
        btn_x = SCREEN_WIDTH - 20 - btn_size
        btn_y = y_center - btn_size // 2
        
        btn_rect = pygame.Rect(btn_x, btn_y, btn_size, btn_size)
        pygame.draw.rect(screen, HEADER_BUTTON_BORDER, btn_rect, border_radius=10)
        inner_btn = btn_rect.inflate(-4, -4)
        pygame.draw.rect(screen, HEADER_BUTTON_YELLOW, inner_btn, border_radius=8)
        
        # Arrow Icon (White)
        arrow_center = btn_rect.center
        # Draw arrow pointing left (Back)
        pygame.draw.polygon(screen, (255, 255, 255), [
            (arrow_center[0] - 8, arrow_center[1]),
            (arrow_center[0] + 4, arrow_center[1] - 8),
            (arrow_center[0] + 4, arrow_center[1] + 8)
        ])
        pygame.draw.rect(screen, (255, 255, 255), (arrow_center[0] + 4, arrow_center[1] - 3, 6, 6))


    def draw_bottom_bar(self, screen, game_state):
        # White Bottom Bar with Rounded Corners
        bar_h = BOTTOM_BAR_HEIGHT
        bar_y = SCREEN_HEIGHT - bar_h
        
        # Shadow/Border top
        pygame.draw.rect(screen, (200, 200, 200), (0, bar_y + 10, SCREEN_WIDTH, bar_h), border_top_left_radius=30, border_top_right_radius=30)
        
        # Main White Body
        bar_rect = pygame.Rect(0, bar_y + 15, SCREEN_WIDTH, bar_h - 15)
        pygame.draw.rect(screen, (245, 245, 245), bar_rect, border_top_left_radius=30, border_top_right_radius=30)
        
        # Power-up Placeholders (Circles)
        # 4 items: 3 powerups + 1 pause/menu
        
        item_count = 4
        item_spacing = SCREEN_WIDTH // (item_count + 1)
        y_center = bar_y + 15 + (bar_h - 15) // 2
        
        icons = ["❄️", "💨", "🧲", "⏸️"]
        colors = [(100, 181, 246), (100, 181, 246), (229, 115, 115), (25, 118, 210)] # Light Blue, Light Blue, Red, Dark Blue
        
        for i in range(item_count):
            x = item_spacing * (i + 1)
            radius = 28
            
            # Circle
            pygame.draw.circle(screen, colors[i], (x, y_center), radius)
            pygame.draw.circle(screen, (255, 255, 255), (x, y_center), radius, 3) # White border
            
            # Icon (Text for now)
            # icon_text = self.font_medium.render(icons[i], True, (255, 255, 255))
            # screen.blit(icon_text, (x - icon_text.get_width()//2, y_center - icon_text.get_height()//2))
            
            # Badge (x3, x2, etc)
            if i < 3:
                badge_text = self.font_tiny.render(f"x{3-i}", True, (100, 100, 100))
                screen.blit(badge_text, (x + 10, y_center + 10))
                
        # Reset Button Logic (Hidden invisible rect over the 4th icon for now to keep functionality?)
        # Or map the 4th icon to Reset/Pause
        
        # Let's map the 4th icon (Pause/Menu) to Reset for now as requested by previous functionality
        self.reset_btn_rect = pygame.Rect(item_spacing * 4 - 30, y_center - 30, 60, 60)
                
    def draw_objectives_panel(self, screen, game_state):
        """Draw objectives panel showing required coins per color"""
        if not hasattr(game_state, 'objectives') or not game_state.objectives:
            return
        
        # Position at top center
        panel_y = 120
        panel_x = SCREEN_WIDTH // 2
        
        # Calculate panel width based on number of objectives
        num_objectives = len(game_state.objectives)
        pill_width = 130  # Width of each pill
        pill_spacing = 10  # Space between pills
        total_width = (pill_width * num_objectives) + (pill_spacing * (num_objectives - 1))
        
        start_x = panel_x - total_width // 2
        
        # Draw each objective indicator
        for i, (color_key, required) in enumerate(game_state.objectives.items()):
            x = start_x + i * (pill_width + pill_spacing)
            
            # Get coin colors from settings
            from core.settings import COIN_COLORS
            colors = COIN_COLORS.get(color_key, COIN_COLORS['YELLOW'])
            
            # Background pill shape (white with dark border for visibility)
            pill_rect = pygame.Rect(x, panel_y, pill_width, 50)
            pygame.draw.rect(screen, (255, 255, 255), pill_rect, border_radius=25)
            pygame.draw.rect(screen, (100, 100, 100), pill_rect, width=3, border_radius=25)
            
            # Draw coin indicator (filled circle with border)
            coin_center = (x + 25, panel_y + 25)
            pygame.draw.circle(screen, colors['fill'], coin_center, 15)
            pygame.draw.circle(screen, colors['border'], coin_center, 15, 3)
            
            # Draw counter text (dark color for visibility)
            counter_text = f"{required}"
            counter_surface = self.font.render(counter_text, True, (40, 40, 40))
            counter_rect = counter_surface.get_rect(center=(x + pill_width - 40, panel_y + 25))
            screen.blit(counter_surface, counter_rect)

    def draw_bottom_bar(self, screen, game_state):
        # Draw Bottom Bar
        bar_height = BOTTOM_BAR_HEIGHT
        bar_y = SCREEN_HEIGHT - bar_height
        bar_rect = pygame.Rect(0, bar_y, SCREEN_WIDTH, bar_height)
        
        # Background (Optional, maybe just transparent or gradient)
        # pygame.draw.rect(screen, (0, 0, 0, 50), bar_rect)

        # Reset Button (Center)
        btn_size = 60
        btn_rect = pygame.Rect((SCREEN_WIDTH - btn_size) // 2, bar_y + (bar_height - btn_size) // 2, btn_size, btn_size)
        
        # Glass Button
        s_btn = pygame.Surface((btn_size, btn_size), pygame.SRCALPHA)
        pygame.draw.circle(s_btn, (255, 255, 255, 30), (btn_size//2, btn_size//2), btn_size//2) # Fill
        pygame.draw.circle(s_btn, (255, 255, 255, 100), (btn_size//2, btn_size//2), btn_size//2, 2) # Border
        
        # Reload Icon (Circular Arrow)
        center = btn_size // 2
        radius = 15
        rect = pygame.Rect(center - radius, center - radius, radius * 2, radius * 2)
        pygame.draw.arc(s_btn, (255, 255, 255), rect, 0.5, 5.8, 3) # Partial circle
        
        # Arrow head
        # Tip of arc is at roughly 0.5 radians (approx 30 deg)
        # Simple triangle
        pygame.draw.polygon(s_btn, (255, 255, 255), [(center + radius, center), (center + radius + 6, center - 6), (center + radius - 6, center - 6)])
        
        screen.blit(s_btn, btn_rect)
        
        # Store rect for click detection
        self.reset_btn_rect = btn_rect
        

        
        # Label (optional, below button)
        # label = self.font_tiny.render("RESET", True, TEXT_COLOR)
        # screen.blit(label, (reset_center[0] - label.get_width()//2, reset_center[1] + 50))

    def draw_message(self, screen, message, stars=None, gold_earned=0, moves=0, time_remaining=0):
        # Overlay (semi-transparent black)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))
        
        # Card (600-700px width, 200-240px height per GDD) - Ensure it fits on screen
        card_width = min(650, SCREEN_WIDTH - 40)
        card_height = min(400, SCREEN_HEIGHT - 40)
        card_rect = pygame.Rect((SCREEN_WIDTH - card_width) // 2, (SCREEN_HEIGHT - card_height) // 2, card_width, card_height)
        pygame.draw.rect(screen, COLOR_WHITE, card_rect, border_radius=16)
        # Shadow
        shadow_rect = card_rect.copy()
        shadow_rect.y += 4
        shadow_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 38))  # rgba(0,0,0,0.15) equivalent
        screen.blit(shadow_surface, shadow_rect)
        pygame.draw.rect(screen, COLOR_WHITE, card_rect, border_radius=16)
        
        # Header (Display Bold, 48-56px per GDD)
        # Header (Display Bold, 48-56px per GDD)
        header_color = BLOCK_COLORS['GREEN']['main'] if stars is not None else BLOCK_COLORS['RED']['main']
        header_text = self.font_large.render(message, True, header_color)
        header_rect = header_text.get_rect(center=(SCREEN_WIDTH // 2, card_rect.top + 50))
        screen.blit(header_text, header_rect)
        
        if stars is not None:
            # Draw Stars (64-72px per GDD, pop animation)
            star_size = 64
            start_x = SCREEN_WIDTH // 2 - (star_size * 1.5)
            star_y = card_rect.top + 120
            
            for i in range(3):
                star_x = start_x + i * (star_size + 20)
                if i < stars:
                    # Earned: Yellow with border
                    pygame.draw.polygon(screen, (255, 214, 107), [  # #FFD66B
                        (star_x, star_y - star_size // 2),
                        (star_x + star_size * 0.2, star_y - star_size * 0.1),
                        (star_x + star_size // 2, star_y),
                        (star_x + star_size * 0.2, star_y + star_size * 0.1),
                        (star_x, star_y + star_size // 2),
                        (star_x - star_size * 0.2, star_y + star_size * 0.1),
                        (star_x - star_size // 2, star_y),
                        (star_x - star_size * 0.2, star_y - star_size * 0.1)
                    ])
                    pygame.draw.polygon(screen, (217, 168, 66), [  # #D9A842 border
                        (star_x, star_y - star_size // 2),
                        (star_x + star_size * 0.2, star_y - star_size * 0.1),
                        (star_x + star_size // 2, star_y),
                        (star_x + star_size * 0.2, star_y + star_size * 0.1),
                        (star_x, star_y + star_size // 2),
                        (star_x - star_size * 0.2, star_y + star_size * 0.1),
                        (star_x - star_size // 2, star_y),
                        (star_x - star_size * 0.2, star_y - star_size * 0.1)
                    ], 2)
                else:
                    # Not earned: Gray outline
                    pygame.draw.polygon(screen, GRID_LINE_COLOR, [
                        (star_x, star_y - star_size // 2),
                        (star_x + star_size * 0.2, star_y - star_size * 0.1),
                        (star_x + star_size // 2, star_y),
                        (star_x + star_size * 0.2, star_y + star_size * 0.1),
                        (star_x, star_y + star_size // 2),
                        (star_x - star_size * 0.2, star_y + star_size * 0.1),
                        (star_x - star_size // 2, star_y),
                        (star_x - star_size * 0.2, star_y - star_size * 0.1)
                    ], 2)
            
            # Statistics Card (per GDD) - Ensure it fits
            stats_y = card_rect.top + 200
            stats_texts = [
                f"Mosse usate: {moves}",
                f"Tempo rimanente: {int(time_remaining // 60):02}:{int(time_remaining % 60):02}",
                f"Monete guadagnate: {gold_earned}"
            ]
            
            # Calculate spacing to fit in card
            stats_spacing = min(35, (card_rect.height - 200 - 60) // len(stats_texts))
            for i, stat_text in enumerate(stats_texts):
                stat_surf = self.font_small.render(stat_text, True, TEXT_COLOR)
                stat_rect = stat_surf.get_rect(center=(SCREEN_WIDTH // 2, stats_y + i * stats_spacing))
                # Ensure text doesn't go outside card
                if stat_rect.bottom < card_rect.bottom - 50:
                    screen.blit(stat_surf, stat_rect)
            
            # Gold earned highlight - ensure it fits
            if gold_earned > 0:
                gold_text = self.font_medium.render(f"+{gold_earned} Gold!", True, BLOCK_COLORS['YELLOW']['main'])
                gold_y = min(card_rect.bottom - 40, SCREEN_HEIGHT - 100)
                gold_rect = gold_text.get_rect(center=(SCREEN_WIDTH // 2, gold_y))
                screen.blit(gold_text, gold_rect)
    
    def draw_menu(self, screen):
        screen.fill(BG_COLOR)
        title = self.font_large.render("TETRACOIN", True, COLOR_PRIMARY_TEAL)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(title, title_rect)
        
        start_text = self.font_medium.render("Tap to Start", True, TEXT_COLOR)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(start_text, start_rect)

    def draw_victory(self, screen, stars=0, moves=0, time_remaining=0, gold_earned=0):
        # Victory screen - draw message first
        self.draw_message(screen, "LIVELLO COMPLETATO!", stars=stars, gold_earned=gold_earned, 
                         moves=moves, time_remaining=time_remaining)
        
        # Add instruction text at bottom of screen (not inside card)
        inst_text = self.font_tiny.render("Premi un tasto o clicca per continuare", True, COLOR_WHITE)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        # Draw with slight shadow for visibility
        shadow_surf = self.font_tiny.render("Premi un tasto o clicca per continuare", True, (0, 0, 0))
        screen.blit(shadow_surf, (inst_rect.x + 2, inst_rect.y + 2))
        screen.blit(inst_text, inst_rect)
    
    def draw_defeat(self, screen, reason="Tempo Scaduto", lives_remaining=0):
        # Defeat screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))
        
        # Card
        card_width = 600
        card_height = 300
        card_rect = pygame.Rect((SCREEN_WIDTH - card_width) // 2, (SCREEN_HEIGHT - card_height) // 2, card_width, card_height)
        pygame.draw.rect(screen, COLOR_WHITE, card_rect, border_radius=16)
        
        # Header
        header_text = self.font_large.render("LIVELLO FALLITO", True, BLOCK_COLORS['RED']['main'])
        header_rect = header_text.get_rect(center=(SCREEN_WIDTH // 2, card_rect.top + 60))
        screen.blit(header_text, header_rect)
        
        # Reason
        reason_text = self.font_medium.render(reason, True, TEXT_COLOR)
        reason_rect = reason_text.get_rect(center=(SCREEN_WIDTH // 2, card_rect.centery))
        screen.blit(reason_text, reason_rect)
        
        # Lives remaining
        if lives_remaining > 0:
            lives_text = self.font_small.render(f"Vite rimanenti: {lives_remaining}", True, TEXT_COLOR)
            lives_rect = lives_text.get_rect(center=(SCREEN_WIDTH // 2, card_rect.bottom - 80))
            screen.blit(lives_text, lives_rect)
        
        # Instructions
        inst_text = self.font_tiny.render("Premi R per riprovare", True, TEXT_COLOR)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, card_rect.bottom - 40))
        screen.blit(inst_text, inst_rect)
    def draw_tutorial(self, screen, text):
        """Draw tutorial text overlay"""
        # Semi-transparent background at the bottom
        overlay_height = 100
        overlay_rect = pygame.Rect(0, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT - overlay_height - 20, SCREEN_WIDTH, overlay_height)
        
        # Draw background with border
        s = pygame.Surface((SCREEN_WIDTH, overlay_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180)) # Dark semi-transparent
        screen.blit(s, overlay_rect.topleft)
        
        # Draw text
        # Wrap text if needed (simple wrapping)
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.font_small.size(test_line)[0] < SCREEN_WIDTH - 40:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        # Render lines
        y = overlay_rect.centery - (len(lines) * 24) // 2
        for line in lines:
            text_surf = self.font_small.render(line, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
            screen.blit(text_surf, text_rect)
            y += 24
