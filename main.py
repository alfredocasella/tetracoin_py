import pygame
import sys
from core.settings import *
from core.game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    
    game = Game()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_input(event)
            
        dt = clock.tick(FPS) / 1000.0
        game.update(dt)
        game.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()
