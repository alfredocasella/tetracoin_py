import pygame
import os

class AudioManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()
        self.combo = 0
        
    def load_sounds(self):
        # Define sound files
        sound_files = {
            'move': 'move.wav',
            'collect_1': 'collect_1.wav',
            'collect_2': 'collect_2.wav',
            'collect_3': 'collect_3.wav',
            'win': 'win.wav',
            'snap': 'snap.wav',
            'fail': 'fail.wav'
        }
        
        for name, filename in sound_files.items():
            path = os.path.join("assets", "audio", filename)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except Exception as e:
                    print(f"Failed to load sound {path}: {e}")
            else:
                print(f"Sound file not found: {path}")

    def play_bgm(self):
        bgm_path = os.path.join("assets", "audio", "bgm.wav")
        if os.path.exists(bgm_path):
            try:
                pygame.mixer.music.load(bgm_path)
                pygame.mixer.music.play(-1) # Loop indefinitely
                pygame.mixer.music.set_volume(0.5)
            except Exception as e:
                print(f"Failed to load BGM: {e}")

    def play_move(self):
        self.combo = 0 # Reset combo on move
        if 'move' in self.sounds:
            self.sounds['move'].play()

    def play_collect(self):
        self.combo += 1
        # Determine pitch level based on combo (1, 2, 3+)
        level = min(self.combo, 3)
        sound_name = f'collect_{level}'
        
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
            
    def play_win(self):
        if 'win' in self.sounds:
            self.sounds['win'].play()
            
    def play_snap(self):
        if 'snap' in self.sounds:
            self.sounds['snap'].play()
            
    def play_fail(self):
        if 'fail' in self.sounds:
            self.sounds['fail'].play()
