import pygame
import os
import wave
import math
import struct
import random

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_images():
    ensure_dir("assets/images")
    pygame.init()
    
    colors = {
        "red": (231, 76, 60),
        "blue": (52, 152, 219),
        "green": (46, 204, 113),
        "yellow": (241, 196, 15),
        "purple": (155, 89, 182)
    }
    
    size = 64
    
    for name, color in colors.items():
        # Block
        surf = pygame.Surface((size, size))
        surf.fill(color)
        pygame.draw.rect(surf, (255, 255, 255), (0, 0, size, size), 2)
        pygame.draw.rect(surf, (0, 0, 0), (2, 2, size-4, size-4), 1)
        pygame.image.save(surf, f"assets/images/block_{name}.png")
        
        # Coin
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (size//2, size//2), size//3)
        pygame.draw.circle(surf, (255, 255, 255), (size//2, size//2), size//3, 2)
        pygame.image.save(surf, f"assets/images/coin_{name}.png")
        
    print("Images generated.")

def generate_audio():
    ensure_dir("assets/audio")
    
    def save_wave(filename, duration, freq, vol=0.5):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        
        with wave.open(filename, 'w') as w:
            w.setparams((1, 2, sample_rate, n_samples, 'NONE', 'not compressed'))
            
            for i in range(n_samples):
                t = i / sample_rate
                # Simple sine wave with decay
                value = int(32767.0 * vol * math.sin(2 * math.pi * freq * t) * (1 - t/duration))
                data = struct.pack('<h', value)
                w.writeframes(data)
                
    save_wave("assets/audio/move.wav", 0.1, 440) # A4
    
    # Collect sounds with rising pitch
    save_wave("assets/audio/collect_1.wav", 0.2, 880) # A5
    save_wave("assets/audio/collect_2.wav", 0.2, 1108) # C#6
    save_wave("assets/audio/collect_3.wav", 0.2, 1318) # E6
    
    save_wave("assets/audio/win.wav", 0.5, 523.25) # C5
    save_wave("assets/audio/snap.wav", 0.05, 220) # A3 (Short snap)
    save_wave("assets/audio/fail.wav", 0.5, 110) # A2 (Low fail)
    
    # Simple BGM (just a longer wave for now, placeholder)
    save_wave("assets/audio/bgm.wav", 2.0, 220, vol=0.1) 
    
    print("Audio generated.")

if __name__ == "__main__":
    generate_images()
    generate_audio()
