import pygame_gui
import pygame
import sys

from pygame_gui.core import ObjectID
from assets.scripts.path_module import path_to_file
from assets.scripts.events import SAVE_AND_RETURN


class ProgressBarWOText(pygame_gui.elements.UIProgressBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def status_text(self):
        return ''


class IngameUI:
    def __init__(self, size, level_number):
        self.screen = pygame.display.get_surface()
        self.manager = pygame_gui.UIManager(
            size, path_to_file('assets', 'uitheme.json'))
        self.timer = None
        self.wave = 0
        self.width = size[0]
        self.height = size[1]

    def initUI(self):
        # ШКАЛА СВЕРХУ
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

        # МЕНЮ СТРОЙКИ
        self.building_panel = pygame_gui.elements.UIPanel(pygame.Rect(-300, 0, 300, self.height // 2),
                                                          manager=self.manager,
                                                          anchors={'right': 'right', 'top': 'top'})
        self.viewport_panel = pygame_gui.elements.UIPanel(pygame.Rect(-300, -self.height // 2, 300, self.height // 2),
                                                          manager=self.manager,
                                                          anchors={'right': 'right', 'bottom': 'bottom'})

        self.itemcontainer2 = pygame_gui.elements.UIScrollingContainer(pygame.Rect(60, 0, 240, self.height // 2),
                                                                       manager=self.manager,
                                                                       container=self.building_panel,
                                                                       parent_element=self.building_panel,
                                                                       visible=False)

        # Индексация
        Placeables = {
            'Harvester': ['Copper drill', 'Hematite drill', 'Titan drill'],
            'Wall': ['Copper wall', 'Titan wall', 'Hematite wall', 'Emerald wall'],
            'Conveyor': ['Conveyor']
        }

        # Создаём кнопки категорий и контейнеры для них
        for i, buttonId in enumerate(('Turret', 'Harvester', 'Energy', 'Wall', 'Conveyor', 'Factory')):
            button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(0, 50 * i, 50, 50),
                                                  text='',
                                                  manager=self.manager,
                                                  container=self.building_panel,
                                                  object_id=ObjectID(object_id=f'#{buttonId}',
                                                                     class_id='@build_categories'))

            container = pygame_gui.elements.UIScrollingContainer(pygame.Rect(60, 0, 240, self.height // 2),
                                                                 manager=self.manager,
                                                                 container=self.building_panel,
                                                                 parent_element=self.building_panel,
                                                                 visible=False)

            setattr(self, f'{buttonId.lower()}_button', button)
            setattr(self, f'{buttonId.lower()}_container', container)

        # Создаём кнопки для каждой из категорий
        for build_type, buildings in Placeables.items():
            container = getattr(self, f'{build_type.lower()}_container')
            for i, build in enumerate(buildings):
                y, x = divmod(i, 4)
                button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(x * 50, y * 50, 50, 50),
                                                      text=build,
                                                      manager=self.manager,
                                                      container=container,
                                                      parent_element=container,
                                                      object_id=ObjectID(object_id=f'#{build.replace(" ", "_")}',
                                                                         class_id='@Place_buttons'))

        # ИНТЕРФЕЙС ПАУЗЫ
        panel_rect = pygame.Rect(0, 0, 160, 160)
        panel_rect.center = (self.width // 2, self.height // 2)
        self.pause_panel = pygame_gui.elements.UIPanel(panel_rect,
                                                       manager=self.manager,
                                                       visible=False)
        pause_kwargs = {'manager': self.manager, 'container': self.pause_panel,
                        'visible': False, 'parent_element': self.pause_panel}
        self.pause_label = pygame_gui.elements.UILabel(pygame.Rect(0, 0, 160, 40),
                                                       text='Paused',
                                                       **pause_kwargs)
        self.unpause_button = pygame_gui.elements.UIButton(pygame.Rect(-4, 40, 161, 40),
                                                           text='Continue',
                                                           **pause_kwargs)
        self.return_button = pygame_gui.elements.UIButton(pygame.Rect(-4, 80, 161, 40),
                                                          text='Save and return',
                                                          **pause_kwargs)
        self.quit_button = pygame_gui.elements.UIButton(pygame.Rect(-4, 120, 161, 40),
                                                        text='Save and quit',
                                                        **pause_kwargs)

        # НАДПИСИ НА ЭКРАНЕ. ПОДСКАЗКИ
        self.hint1 = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, -20, 228, 20),
                                                 text='B/TAB - open building menu',
                                                 manager=self.manager,
                                                 anchors={'centerx': 'centerx', 'bottom': 'bottom'})

        self.hint2 = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, -41, 228, 20),
                                                 text='Esc - pause menu',
                                                 manager=self.manager,
                                                 anchors={'centerx': 'centerx', 'bottom': 'bottom'})

        # ИНТЕРФЕЙС РЕСУРСОВ
        spritesheet = pygame.image.load(os.path.join('assets', 'sprites', 'ResourceIcons.png')).convert_alpha()
        icon_surfaces = list()
        for x in range(5):
            surf = pygame.Surface((50, 50)).convert_alpha()
            surf.blit(spritesheet, (0, 0), (x * 50, 0, 50, 50))
            icon_surfaces.append(surf)
            

        self.text1 = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 0, 300, 50),
                                                 text='Resources in base:',
                                                 container=self.viewport_panel,
                                                 parent_element=self.viewport_panel,
                                                 manager=self.manager)
        for i, name in enumerate(('Titan', 'Coal', 'Hematite', 'Emerald', 'Copper')):
            icon = pygame_gui.elements.UIImage(relative_rect=pygame.Rect(0, 50 * i + 50, 50, 50),
                                               image_surface=icon_surfaces[i],
                                               manager=self.manager,
                                               container=self.viewport_panel,
                                               parent_element=self.viewport_panel)
            text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(50, 50 * i + 50, 250, 50),
                                               manager=self.manager,
                                               container=self.viewport_panel,
                                               parent_element=self.viewport_panel,
                                               text=f'{name}: 0')

            setattr(self, f'icon{i + 1}', icon)
            setattr(self, f'{name}Text', text)

    def update_resource_amounts(self, resource_dict):
        for key, value in resource_dict.items():
            text = getattr(self, f'{key}Text')
            text.set_text(f'{key}: {value}')

    def show_build_container(self, name):
        self.turret_container.hide()
        self.harvester_container.hide()
        self.wall_container.hide()
        self.energy_container.hide()
        self.conveyor_container.hide()
        self.factory_container.hide()
        getattr(self, name).show()

    def pause_game(self):
        temp_clock = pygame.time.Clock()
        self.pause_panel.show()

        self.screen = pygame.display.get_surface()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return self.pause_panel.hide()
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.unpause_button:
                        return self.pause_panel.hide()
                    elif event.ui_element == self.return_button:
                        return pygame.event.post(SAVE_AND_RETURN)
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
