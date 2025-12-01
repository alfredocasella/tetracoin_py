import pygame
import math
from settings import *

class UI:
    def __init__(self):
        self.font_large = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_tiny = pygame.font.SysFont("Arial", 18, bold=True)
        
        # Animation state for timer pulse
        self.timer_pulse_time = 0
        
        # Load icons (placeholders for now, drawing shapes instead)
    
    def update(self, dt):
        """Update UI animations"""
        self.timer_pulse_time += dt * 10  # Increment pulse animation
        
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
        # Glassmorphism Objectives Panel
        panel_h = 60
        panel_y = TOP_HUD_HEIGHT + 10
        
        # Title "Obiettivi" - Small and elegant
        font_title = pygame.font.SysFont("Arial", 14, bold=True)
        title_surf = font_title.render("OBIETTIVI", True, TEXT_COLOR)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, panel_y))
        screen.blit(title_surf, title_rect)
        
        # Objectives Container
        container_y = panel_y + 15
        
        # Calculate width
        total_w = 0
        gap = 15
        
        # Prepare surfaces
        pill_surfs = []
        
        for i, (color, required) in enumerate(game_state.objectives.items()):
            collected = game_state.coins_collected_per_color.get(color, 0)
            is_complete = collected >= required
            
            # Pill dimensions
            pill_w = 90
            pill_h = 32
            
            s_pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
            
            # Background (Glass)
            bg_color = (255, 255, 255, 150)
            border_color = (255, 255, 255, 200)
            if is_complete:
                bg_color = (100, 255, 100, 150)
                border_color = (100, 255, 100, 200)
                
            pygame.draw.rect(s_pill, bg_color, (0, 0, pill_w, pill_h), border_radius=16)
            pygame.draw.rect(s_pill, border_color, (0, 0, pill_w, pill_h), 1, border_radius=16)
            
            # Icon (Circle with color)
            pygame.draw.circle(s_pill, COLORS.get(color, (200, 200, 200)), (16, 16), 8)
            
            # Text
            font_obj = pygame.font.SysFont("Arial", 16, bold=True)
            text = f"{collected}/{required}"
            text_surf = font_obj.render(text, True, TEXT_COLOR)
            text_rect = text_surf.get_rect(midleft=(32, 16))
            s_pill.blit(text_surf, text_rect)
            
            # Checkmark if complete
            if is_complete:
                # Simple checkmark
                pygame.draw.line(s_pill, TEXT_COLOR, (pill_w - 20, 16), (pill_w - 16, 20), 2)
                pygame.draw.line(s_pill, TEXT_COLOR, (pill_w - 16, 20), (pill_w - 10, 10), 2)
            
            pill_surfs.append(s_pill)
            total_w += pill_w + gap
            
        if total_w > 0:
            total_w -= gap # Remove last gap
        
        # Draw centered
        start_x = (SCREEN_WIDTH - total_w) // 2
        current_x = start_x
        
        for s in pill_surfs:
            screen.blit(s, (current_x, container_y))
            current_x += s.get_width() + gap

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
