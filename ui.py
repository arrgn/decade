import pygame_gui
import pygame
import sys
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
        self.manager = pygame_gui.UIManager(
            size, path_to_file('assets', 'uitheme.json'))
        self.timer = None
        self.wave = 0
        self.width = size[0]
        self.height = size[1]

    def initUI(self):

        # Главный интерфейс
        panel_rect = pygame.Rect(0, 0, 300, 100)
        panel_rect.midtop = (self.width // 2, 0)
        self.panel = pygame_gui.elements.UIPanel(
            panel_rect, manager=self.manager)
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

        # Интерфейс паузы
        panel_rect = pygame.Rect(0, 0, 160, 160)
        panel_rect.center = (self.width // 2, self.height // 2)
        self.pause_panel = pygame_gui.elements.UIPanel(panel_rect,
                                                       manager=self.manager,
                                                       visible=False)
        pause_kwargs = {'manager': self.manager, 'container': self.pause_panel,
                        'visible': False, 'parent_element': self.pause_panel}
        self.pause_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 0, 160, 40),
                                                       text='Paused',
                                                       **pause_kwargs)
        self.unpause_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(-4, 40, 161, 40),
                                                           text='Continue',
                                                           **pause_kwargs)
        self.return_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(-4, 80, 161, 40),
                                                          text='Save and return',
                                                          **pause_kwargs)
        self.quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(-4, 120, 161, 40),
                                                        text='Save and quit',
                                                        **pause_kwargs)

    def set_pausemenu_visible(self, state):
        self.pause_panel.visible = state
        self.pause_label.visible = state
        self.unpause_button.visible = state
        self.return_button.visible = state
        self.quit_button.visible = state

    def pause_game(self):
        temp_clock = pygame.time.Clock()
        self.set_pausemenu_visible(True)

        self.screen = pygame.display.get_surface()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return self.set_pausemenu_visible(False)
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.unpause_button:
                        return self.set_pausemenu_visible(False)
                    elif event.ui_element == self.quit_button:
                        pygame.quit()
                        sys.exit(0)

                dt = temp_clock.tick(30)
                self.manager.process_events(event)
                self.manager.update(dt / 1000)
                self.manager.draw_ui(self.screen)
                pygame.display.update()

    def start_timer(self, secs):
        self.timer = secs
        self.secs_elapsed = 0

    def convert_to_timestring(self, secs):
        minutes, seconds = divmod(secs, 60)
        return f'{int(minutes)}:{str(int(seconds)).zfill(2)}'

    def update_timer(self, dt):
        if self.timer:
            self.secs_elapsed += dt / 1000
            secs_remaining = self.timer - self.secs_elapsed
            if secs_remaining < 0:
                self.timer = None
                self.secs_elapsed = 0
                self.wave += 1
                self.progress_text.set_text(
                    f'Wave {self.wave}/10 Remaining enemies: N/A')
            else:
                self.progress_text.set_text(
                    f'Wave {self.wave}/10 Time remaining: {self.convert_to_timestring(secs_remaining)}')
                self.progress_bar.set_current_progress(
                    self.secs_elapsed / self.timer)

    def update_UI(self, dt):
        self.update_timer(dt)
        self.manager.update(dt / 1000)
        self.manager.draw_ui(self.screen)


class MainMenuUI:
    def __init__(self, size):
        # , path_to_file('assets', 'uitheme.json'))
        self.manager = pygame_gui.UIManager(size)
        self.width = size[0]
        self.height = size[1]
