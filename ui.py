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
        
    def draw(self, screen, level_id, blocks_remaining, coins_remaining, time_remaining, move_count, gold=0, total_stars=0, lives=5, objectives=None, timer_state="NORMAL"):
        # 1. Draw Top HUD
        self.draw_top_hud(screen, level_id, time_remaining, lives, gold, timer_state)
        
        # 2. Draw Grid Area Background (Optional, helps visualize layout)
        # grid_area_rect = pygame.Rect(0, TOP_HUD_HEIGHT, SCREEN_WIDTH, GRID_AREA_HEIGHT)
        # pygame.draw.rect(screen, BG_COLOR, grid_area_rect)
        
        # 3. Draw Objective Panel
        self.draw_objectives_panel(screen, objectives)
        
        # 4. Draw Bottom Bar
        self.draw_bottom_bar(screen)

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
            time_color = COLOR_WARNING_ORANGE
            pulse_scale = 1.0
        elif timer_state == "CRITICAL": 
            time_color = COLOR_ERROR_RED
            # Pulse animation for critical state
            pulse_scale = 1.0 + 0.1 * math.sin(self.timer_pulse_time * 10)
        else:
            pulse_scale = 1.0
            
        # Timer Pillola
        pill_width = 280
        pill_height = 56
        pill_rect = pygame.Rect(SCREEN_WIDTH // 2 - pill_width // 2, 20, pill_width, pill_height)
        
        # Apply pulse scale if critical
        if timer_state == "CRITICAL" and pulse_scale > 1.0:
            pill_rect = pill_rect.inflate((pulse_scale - 1.0) * pill_width, (pulse_scale - 1.0) * pill_height)
            pill_rect.centerx = SCREEN_WIDTH // 2
            pill_rect.centery = 20 + pill_height // 2
        
        # Draw pillola background
        pygame.draw.rect(screen, COLOR_WHITE, pill_rect, border_radius=28)
        pygame.draw.rect(screen, GRID_CONTAINER_BORDER, pill_rect, 2, border_radius=28)
        
        # Clock icon (24x24px per GDD)
        clock_icon_size = 24
        clock_x = pill_rect.left + 16
        clock_y = pill_rect.centery
        pygame.draw.circle(screen, COLOR_PRIMARY_TEAL, (clock_x, clock_y), clock_icon_size // 2, 2)
        # Clock hands
        pygame.draw.line(screen, COLOR_PRIMARY_TEAL, (clock_x, clock_y), (clock_x, clock_y - 6), 2)
        pygame.draw.line(screen, COLOR_PRIMARY_TEAL, (clock_x, clock_y), (clock_x + 4, clock_y), 2)
        
        # Timer text (Bold, 32px per GDD)
        time_surf = self.font_medium.render(time_str, True, time_color)
        time_rect = time_surf.get_rect(center=(pill_rect.centerx, pill_rect.centery))
        screen.blit(time_surf, time_rect)
        
        # Right section: Lives, Gold, and Pause Button
        # Pause Button (Top Right, 56x56px per GDD) - Priority position
        pause_size = 56
        pause_rect = pygame.Rect(SCREEN_WIDTH - pause_size - 20, 20, pause_size, pause_size)
        
        # Lives and Gold (to the left of pause button, vertically stacked)
        right_x = pause_rect.left - 20
        
        # Lives (Top right)
        heart_size = 24
        heart_y = 30
        if right_x > SCREEN_WIDTH // 2:  # Only show if there's space
            pygame.draw.circle(screen, COLOR_ERROR_RED, (right_x - heart_size, heart_y), heart_size // 2)
            lives_text = self.font_small.render(f"x {lives}", True, TEXT_COLOR)
            lives_text_x = right_x - heart_size - lives_text.get_width() - 5
            if lives_text_x > badge_rect.right + 100:  # Ensure no overlap with level text
                screen.blit(lives_text, (lives_text_x, heart_y - lives_text.get_height() // 2))
        
        # Gold (Below lives)
        coin_size = 24
        coin_y = 60
        if right_x > SCREEN_WIDTH // 2:  # Only show if there's space
            pygame.draw.circle(screen, COLOR_WARNING_ORANGE, (right_x - coin_size, coin_y), coin_size // 2)
            gold_text = self.font_small.render(f"{gold:,}", True, TEXT_COLOR)
            gold_text_x = right_x - coin_size - gold_text.get_width() - 5
            if gold_text_x > badge_rect.right + 100:  # Ensure no overlap
                screen.blit(gold_text, (gold_text_x, coin_y - gold_text.get_height() // 2))
        pygame.draw.circle(screen, COLOR_PRIMARY_TEAL, pause_rect.center, pause_size // 2)
        
        # Pause Icon (32px per GDD)
        icon_size = 32
        icon_rect = pygame.Rect(0, 0, icon_size, icon_size)
        icon_rect.center = pause_rect.center
        pygame.draw.rect(screen, COLOR_WHITE, (icon_rect.left, icon_rect.top, 8, icon_size), border_radius=2)
        pygame.draw.rect(screen, COLOR_WHITE, (icon_rect.right - 8, icon_rect.top, 8, icon_size), border_radius=2)

    def draw_objectives_panel(self, screen, objectives):
        # Calculate panel position to avoid overlap
        panel_y = TOP_HUD_HEIGHT + GRID_AREA_HEIGHT
        # Ensure panel doesn't go off screen
        if panel_y + OBJECTIVE_PANEL_HEIGHT > SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT:
            panel_y = SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT - OBJECTIVE_PANEL_HEIGHT
        panel_rect = pygame.Rect(0, panel_y, SCREEN_WIDTH, OBJECTIVE_PANEL_HEIGHT)
        
        # Title (Bold, 32px per GDD)
        title_text = self.font_medium.render("Obiettivi", True, TEXT_COLOR)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, panel_y + 10))
        
        if objectives:
            # Draw pills for each color (200x72px per GDD)
            start_x = 20
            pill_width = 200
            pill_height = 72
            gap = 16
            
            # Center pills horizontally
            total_width = len(objectives) * pill_width + (len(objectives) - 1) * gap
            start_x = (SCREEN_WIDTH - total_width) // 2
            
            # Color-specific pastel backgrounds per GDD
            pastel_colors = {
                "YELLOW": (255, 232, 163),  # #FFE8A3
                "BLUE": (215, 227, 255),    # #D7E3FF
                "RED": (255, 209, 209),     # #FFD1D1
                "GREEN": (196, 241, 221),   # #C4F1DD
                "PURPLE": (228, 209, 255)   # #E4D1FF
            }
            
            for i, (color_name, data) in enumerate(objectives.items()):
                collected = data['collected']
                required = data['required']
                color_rgb = COLORS.get(color_name, (100, 100, 100))
                pastel_bg = pastel_colors.get(color_name, COLOR_WHITE)
                
                x = start_x + i * (pill_width + gap)
                y = panel_y + 50
                
                # Pill bg (200x72px, raggio 36px per GDD)
                pill_rect = pygame.Rect(x, y, pill_width, pill_height)
                pygame.draw.rect(screen, pastel_bg, pill_rect, border_radius=36)
                pygame.draw.rect(screen, color_rgb, pill_rect, 2, border_radius=36)
                
                # Coin icon (32-40px per GDD)
                icon_size = 36
                icon_x = x + 20
                icon_y = y + pill_height // 2
                pygame.draw.circle(screen, color_rgb, (icon_x, icon_y), icon_size // 2)
                # Inner highlight
                pygame.draw.circle(screen, pastel_bg, (icon_x - 4, icon_y - 4), icon_size // 4)
                
                # Text "x collected / required" (Bold, 28px per GDD)
                text = f"{collected} / {required}"
                text_surf = self.font_small.render(text, True, TEXT_COLOR)
                text_rect = text_surf.get_rect(center=(pill_rect.centerx, pill_rect.centery))
                screen.blit(text_surf, text_rect)
                
                # Checkmark if complete (right side)
                if collected >= required:
                    check_x = x + pill_width - 20
                    check_y = y + 20
                    # Green checkmark circle
                    pygame.draw.circle(screen, COLOR_SUCCESS_GREEN, (check_x, check_y), 12)
                    # White checkmark
                    pygame.draw.line(screen, COLOR_WHITE, (check_x - 4, check_y), (check_x - 1, check_y + 3), 3)
                    pygame.draw.line(screen, COLOR_WHITE, (check_x - 1, check_y + 3), (check_x + 4, check_y - 2), 3)
                else:
                    # Incomplete: gray circle outline
                    check_x = x + pill_width - 20
                    check_y = y + 20
                    pygame.draw.circle(screen, GRID_LINE_COLOR, (check_x, check_y), 12, 2)

    def draw_bottom_bar(self, screen):
        bar_y = SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT
        bar_rect = pygame.Rect(0, bar_y, SCREEN_WIDTH, BOTTOM_BAR_HEIGHT)
        
        # Background with rounded top corners (#DCE7F9 per GDD)
        bg_color = (220, 231, 249)  # #DCE7F9
        pygame.draw.rect(screen, bg_color, bar_rect, border_top_left_radius=24, border_top_right_radius=24)
        
        # Reset Button (Center, 80-88px per GDD)
        reset_size = 80
        reset_center = (SCREEN_WIDTH // 2, bar_y + BOTTOM_BAR_HEIGHT // 2)
        # Background with 80% opacity teal
        reset_surface = pygame.Surface((reset_size, reset_size), pygame.SRCALPHA)
        reset_color = (*COLOR_PRIMARY_TEAL, 204)  # 80% opacity
        pygame.draw.circle(reset_surface, reset_color, (reset_size // 2, reset_size // 2), reset_size // 2)
        screen.blit(reset_surface, (reset_center[0] - reset_size // 2, reset_center[1] - reset_size // 2))
        
        # Icon (Refresh arrow - white)
        icon_radius = 30
        # Draw circular arrow
        pygame.draw.arc(screen, COLOR_WHITE, 
                       (reset_center[0] - icon_radius, reset_center[1] - icon_radius, 
                        icon_radius * 2, icon_radius * 2), 
                       0.5, 5.5, 4)
        # Arrow head
        arrow_x = reset_center[0] + icon_radius * 0.7
        arrow_y = reset_center[1] - icon_radius * 0.3
        pygame.draw.polygon(screen, COLOR_WHITE, [
            (arrow_x, arrow_y),
            (arrow_x - 8, arrow_y - 4),
            (arrow_x - 8, arrow_y + 4)
        ])
        
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
        header_text = self.font_large.render(message, True, COLOR_SUCCESS_GREEN if stars is not None else COLOR_ERROR_RED)
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
                gold_text = self.font_medium.render(f"+{gold_earned} Gold!", True, COLOR_WARNING_ORANGE)
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
        header_text = self.font_large.render("LIVELLO FALLITO", True, COLOR_ERROR_RED)
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
