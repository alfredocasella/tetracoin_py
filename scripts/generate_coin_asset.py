"""
Generate greyscale base coin sprite for color tinting
This creates a "stacked coins" sprite that can be tinted to any color
"""
import pygame
import sys
import os

# Initialize pygame
pygame.init()

# Sprite size
SPRITE_SIZE = 50

# Create surface
sprite = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
sprite.fill((0, 0, 0, 0))

center_x = SPRITE_SIZE // 2

# Greyscale values for 3D effect
white = (255, 255, 255)
light_grey = (200, 200, 200)
mid_grey = (150, 150, 150)
dark_grey = (100, 100, 100)
darker_grey = (70, 70, 70)

# Coin parameters
disc_radius = (SPRITE_SIZE - 8) // 2
num_discs = 6  # More discs for better stack
disc_thickness = 2
disc_spacing = 2

# Start from bottom
base_y = SPRITE_SIZE - 4

# Shadow
shadow_rect = pygame.Rect(center_x - disc_radius - 1, base_y + 1,
                          disc_radius * 2 + 2, 4)
pygame.draw.ellipse(sprite, (40, 40, 40, 150), shadow_rect)

# Draw each disc from bottom to top
for i in range(num_discs):
    disc_y = base_y - (i * (disc_thickness + disc_spacing))
    
    # Disc edge (dark)
    edge_rect = pygame.Rect(center_x - disc_radius, disc_y,
                           disc_radius * 2, disc_thickness)
    pygame.draw.rect(sprite, dark_grey, edge_rect)
    
    # Rounded left side
    pygame.draw.circle(sprite, dark_grey,
                     (center_x - disc_radius, disc_y + disc_thickness // 2),
                     disc_thickness // 2)
    # Rounded right side
    pygame.draw.circle(sprite, dark_grey,
                     (center_x + disc_radius, disc_y + disc_thickness // 2),
                     disc_thickness // 2)
    
    # Top face (light grey - this will be tinted)
    top_y = disc_y - 1
    top_rect = pygame.Rect(center_x - disc_radius, top_y,
                          disc_radius * 2, disc_thickness + 2)
    pygame.draw.ellipse(sprite, light_grey, top_rect)
    
    # Rim (white highlight)
    pygame.draw.ellipse(sprite, white, top_rect, 1)
    
    # Inner highlight on top 2 discs
    if i >= num_discs - 2:
        highlight_rect = pygame.Rect(center_x - disc_radius // 2, top_y + 1,
                                    disc_radius, disc_thickness)
        pygame.draw.ellipse(sprite, white, highlight_rect, 1)

# Save sprite
output_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'coin_stack_base.png')

pygame.image.save(sprite, output_path)
print(f"✓ Generated greyscale coin sprite: {output_path}")

# Show preview
print("\nPreview: Press any key to close...")
screen = pygame.display.set_mode((200, 200))
pygame.display.set_caption("Coin Stack Preview")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            running = False
    
    screen.fill((200, 230, 255))
    screen.blit(sprite, (75, 75))
    pygame.display.flip()

pygame.quit()
