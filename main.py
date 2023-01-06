import logging.config
import sys
import traceback
import pygame
from PyQt5 import Qt

from button import Button, ButtonGroup, ButtonImage
from config import user, release
from assets.scripts.path_module import path_to_file, create_dir, copy_file, path_to_userdata
from assets.scripts.loggers import logger
from assets.scripts.auth_window import AuthWindow
from assets.scripts.profile_window import ProfileWindow


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

        # Создаём спрайты
        profile_sprite = pygame.image.load(path_to_userdata(user.get_avatar(), str(user.get_user_id()))).convert_alpha()

        # Создаём кнопки и добавляем их в группу
        profile_button = ButtonImage((1210, 10, 60, 60), profile_sprite)
        play_button = Button((50, 200, 200, 50), 'Play', font, 'White', '#0496FF', '#006BA6')
        options_button = Button((50, 275, 200, 50), 'Options', font, 'White', '#0496FF', '#006BA6')
        exit_button = Button((50, 350, 200, 50), 'Exit', font, 'White', '#0496FF', '#006BA6')
        sign_in_button = Button((1210, 80, 60, 35), 'Sign In', small_font, 'White', '#0496FF', '#006BA6')
        sign_up_button = Button((1210, 125, 60, 35), 'Sign Un', small_font, 'White', '#0496FF', '#006BA6')
        logout_button = Button((1210, 170, 60, 35), 'Logout', small_font, 'White', '#0496FF', '#006BA6')
        menu_buttons = ButtonGroup(play_button, profile_button, options_button, exit_button, sign_in_button,
                                   sign_up_button, logout_button)

        # Запускаем музочку.
        pygame.mixer.music.load(path_to_file('assets', 'music', 'Waterfall.mp3'))
        pygame.mixer.music.play(3)
        pygame.mixer.music.set_volume(0)

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
                        elif clicked_button is options_button:
                            print('Нажата кнопка НАСТРОЙКИ')
                        elif clicked_button is profile_button:
                            print('Нажата кнопка ПРОФИЛЬ')
                            ProfileWindow().exec()
                            # Перезагружаем аватарку
                            profile_sprite = pygame.image.load(
                                path_to_userdata(user.get_avatar(), str(user.get_user_id()))).convert_alpha()
                            profile_button.set_image(profile_sprite)
                        elif clicked_button is sign_in_button or clicked_button is sign_up_button:
                            print('Нажата кнопка SIGN ' + ('IN' if clicked_button is sign_in_button else 'UP'))
                            AuthWindow(clicked_button is sign_in_button).exec()
                            # Перезагружаем аватарку
                            profile_sprite = pygame.image.load(
                                path_to_userdata(user.get_avatar(), str(user.get_user_id()))).convert_alpha()
                            profile_button.set_image(profile_sprite)
                        elif clicked_button is logout_button:
                            print('Нажата кнопка LOGOUT')
                            user.log_out()
                            # Перезагружаем аватарку
                            profile_sprite = pygame.image.load(
                                path_to_userdata(user.get_avatar(), str(user.get_user_id()))).convert_alpha()
                            profile_button.set_image(profile_sprite)
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


def log_handler(exctype, value, tb):
    """
    Custom exception handler.
    All critical errors will be logged with tag [ERROR]
    """
    logger.exception(''.join(traceback.format_exception(exctype, value, tb)))


if __name__ == "__main__":
    # Create folder for log and load log configuration
    create_dir("logs")
    create_dir("userdata", "default")
    copy_file(path_to_file("assets", "images", "default.png"), "default")

    logging.config.fileConfig(fname=path_to_file("logging.conf"), disable_existing_loggers=False)
    if release:
        logging.disable(level=logging.WARNING)
    sys.excepthook = log_handler

    app = Qt.QApplication([])
    main_window = Game(1280, 720)
    main_window.run()
    app.exec()
