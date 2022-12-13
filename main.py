import sys
import pygame
from button import Button, ButtonGroup


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
        unscaledBg = pygame.image.load('assets/images/MainMenuBg.jpg').convert()
        bg = pygame.transform.scale(unscaledBg, pygame.display.get_window_size())

        # Отрисовываем название игры сверху
        bigFont = pygame.font.Font('assets/fonts/CinnamonCoffeCake.ttf', 100)
        textSurface = bigFont.render('Untitled game', True, 'White')

        # Создаём кнопки и добавляем их в группу
        font = pygame.font.Font('assets/fonts/CinnamonCoffeCake.ttf', 35)
        playButton = Button((50, 200, 200, 50), 'Play', font, 'White', '#0496FF', '#006BA6')
        optionsButton = Button((50, 275, 200, 50), 'Options', font, 'White', '#0496FF', '#006BA6')
        exitButton = Button((50, 350, 200, 50), 'Exit', font, 'White', '#0496FF', '#006BA6')
        menuButtons = ButtonGroup(playButton, exitButton, optionsButton)

        # Запускаем музочку.
        pygame.mixer.music.load('assets/music/Waterfall.mp3')
        pygame.mixer.music.play(3)

        # Main loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEMOTION:
                    menuButtons.checkHover(event.pos)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Проверяем, нажата ли левая кнопка мыши, и находится ли курсор над кнопкой.
                    if event.button == pygame.BUTTON_LEFT:
                        clickedButton = menuButtons.checkClick(event.pos)
                        if clickedButton is None: continue

                        if clickedButton is playButton:
                            print('Нажата кнопка ИГРАТЬ')
                        elif clickedButton is optionsButton:
                            print('Нажата кнопка НАСТРОЙКИ')
                        elif clickedButton is exitButton:
                            print('Нажата кнопка ВЫХОД')

            # Рисуем сначала фон, потом кнопки на нём.
            self.screen.blit(bg, (0, 0))
            self.screen.blit(textSurface, (50, 0))
            menuButtons.update(self.screen)

            self.clock.tick(self.FPS)
            pygame.display.update()


if __name__ == "__main__":
    mainWindow = Game(1280, 720)
    mainWindow.run()