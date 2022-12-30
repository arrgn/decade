import pygame_gui
import pygame
from pygame_gui.core import ObjectID
from assets.scripts.path_module import path_to_file


class ProgressBarWOText(pygame_gui.elements.UIProgressBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def status_text(self):
        return ''


class IngameUI:
    def __init__(self, size):
        self.screen = pygame.display.get_surface()
        self.manager = pygame_gui.UIManager(size, path_to_file('assets', 'uitheme.json'))
        self.timer = None
        self.wave = 0
        self.width = size[0]
        self.height = size[1]

    def initUI(self):
        panel_rect = pygame.Rect(0, 0, 300, 100)
        panel_rect.midtop = (self.width // 2, 0)
        self.panel = pygame_gui.elements.UIPanel(panel_rect, manager=self.manager)
        self.progress_bar = ProgressBarWOText(pygame.Rect(0, 10, 295, 25),
                                      manager=self.manager,
                                      container=self.panel,
                                      object_id=ObjectID('toppanel', 'panel'))
        self.progress_bar.set_current_progress(100)
        self.progress_text = pygame_gui.elements.UILabel(pygame.Rect(0, 35, 300, 25),
                                                              text=f'Wave {self.wave}/10 Time remaining: 5:00',
                                                              manager=self.manager,
                                                              container=self.panel,
                                                              object_id=ObjectID('toplabel', 'label'))
    
    def startTimer(self, secs):
        self.timer = secs
        self.secsElapsed = 0

    def convert_to_timestring(self, secs):
        minutes, seconds = divmod(secs, 60)
        return f'{int(minutes)}:{str(int(seconds)).zfill(2)}'

    def updateTimer(self, dt):
        if self.timer:
            self.secsElapsed += dt / 1000
            secsRemaining = self.timer - self.secsElapsed
            if secsRemaining < 0:
                self.timer = None
                self.secsElapsed = 0
                self.wave += 1
                self.progress_text.set_text(f'Wave {self.wave}/10 Remaining enemies: N/A')
            else:
                self.progress_text.set_text(f'Wave {self.wave}/10 Time remaining: {self.convert_to_timestring(secsRemaining)}')
                self.progress_bar.set_current_progress(self.secsElapsed / self.timer)

    def updateUI(self, dt):
        self.updateTimer(dt)
        self.manager.update(dt / 1000)
        self.manager.draw_ui(self.screen)




class MainMenuUI:
    def __init__(self, size):
        self.manager = pygame_gui.UIManager(size)#, path_to_file('assets', 'uitheme.json'))
        self.width = size[0]
        self.height = size[1]