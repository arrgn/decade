import sys
import pygame
from button import Button, ButtonGroup
from assets.scripts.path_module import path_to_file
from pytmx.util_pygame import load_pygame


class Cell:
    def __init__(self) -> None:
        pass


class Board:
    def __init__(self, rows, columns):
        self.left = 0
        self.top = 0
        self.width = columns
        self.height = rows
        self.cell_size = 30
        self.board = self.getBoard()

    def getBoard(self):
        blocks = list()
        for _ in range(self.width):
            block = list()
            for _ in range(self.height):
                block.append(Cell())
            blocks.append(block)
        return blocks

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def get_click(self, pos):
        offsetPos = (pos[0] - self.left, pos[1] - self.top)
        coords = (offsetPos[0] // self.cell_size,
                  offsetPos[1] // self.cell_size)
        if 0 <= coords[0] < self.width and 0 <= coords[1] < self.height:
            return coords
        return None

    def render(self, screen):
        for x in range(self.width):
            for y in range(self.height):
                xPos = self.left + self.cell_size * x
                yPos = self.top + self.cell_size * y
                rect = pygame.Rect(xPos, yPos, self.cell_size, self.cell_size)
                pygame.draw.rect(screen, 'Gray', rect, 1)


class Game:
    FPS = 60

    def __init__(self, width, height) -> None:
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        pygame.display.set_caption('Untitled')
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        pygame.display.update()

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.show_menu()
            # TODO Далее этого скрипт пока не проходит.             TODO
            # TODO Здесь можно будет отрисовывать другие экраны.    TODO

            self.clock.tick(self.FPS)
            pygame.display.update()

    def show_menu(self):
        # Масштабируем задний фон под размеры окна
        unscaled_bg = pygame.image.load(path_to_file('assets', 'images', 'MainMenuBg.jpg')).convert()
        bg = pygame.transform.scale(unscaled_bg, pygame.display.get_window_size())

        # Отрисовываем тексты
        small_font = pygame.font.Font(path_to_file('assets', 'fonts', 'CinnamonCoffeCake.ttf'), 20)
        font = pygame.font.Font(path_to_file('assets', 'fonts', 'CinnamonCoffeCake.ttf'), 35)
        big_font = pygame.font.Font(path_to_file('assets', 'fonts', 'CinnamonCoffeCake.ttf'), 100)
        game_title = big_font.render('Untitled game', True, '#E1FAF9')
        version_title = small_font.render('Version Prealpha 0.1', True, '#E1FAF9')

        # Создаём кнопки и добавляем их в группу
        play_button = Button((50, 200, 200, 50), 'Play', font, 'White', '#0496FF', '#006BA6')
        options_button = Button((50, 275, 200, 50), 'Options', font, 'White', '#0496FF', '#006BA6')
        exit_button = Button((50, 350, 200, 50), 'Exit', font, 'White', '#0496FF', '#006BA6')
        menu_buttons = ButtonGroup(play_button, options_button, exit_button)

        # Запускаем музочку.
        pygame.mixer.music.load(path_to_file('assets', 'music', 'Waterfall.mp3'))
        pygame.mixer.music.play(3)
        pygame.mixer.music.set_volume(0.2)

        # Main loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEMOTION:
                    menu_buttons.check_hover(event.pos)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Проверяем, нажата ли левая кнопка мыши, и находится ли курсор над кнопкой.
                    if event.button == pygame.BUTTON_LEFT:
                        clicked_button = menu_buttons.check_click(event.pos)
                        if clicked_button is None: continue

                        if clicked_button is play_button:
                            print('Нажата кнопка ИГРАТЬ')
                            self.play_screen()
                        elif clicked_button is options_button:
                            print('Нажата кнопка НАСТРОЙКИ')
                        elif clicked_button is exit_button:
                            print('Нажата кнопка ВЫХОД')

            # Отрисовываем всё по порядку
            self.screen.blit(bg, (0, 0))
            pygame.draw.rect(self.screen, '#EE6C4D', game_title.get_rect(topleft=(50, 20)))
            self.screen.blit(game_title, (50, 20))
            self.screen.blit(version_title, version_title.get_rect(bottomright=(pygame.display.get_window_size())))
            menu_buttons.update(self.screen)

            self.clock.tick(self.FPS)
            pygame.display.update()

    def play_screen(self):

        # board = Board(3, 10)
        # board.set_view(0, 0, 100)

        # self.screen.fill(0)
        # board.render(self.screen)
        tmx_data = load_pygame('assets/maps/Map.tmx')
        print(dir(tmx_data))
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            self.clock.tick(self.FPS)
            pygame.display.update()


if __name__ == "__main__":
    main_window = Game(1280, 720)
    main_window.run()
