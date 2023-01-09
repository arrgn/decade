import logging.config
import sys
import traceback
import pygame_gui

from assets.scripts.path_module import create_dir, copy_file, path_to_userdata, path_to_asset, path_to_file

if __name__ == "__main__":
    """
        Прикол в том, что при создании юзера мы копируем дефолтные файлы из папки userdata/default.
        Если разместить этот код после импорта юзера/окна авторизации - вылезет ошибка, так как юзер не сможет
        копировать файлы либо окно авторизации не сможет открыть  файл.
        В этом месте лучше копировать все необходимые файлы по умолчанию для юзера.
    """
    create_dir("userdata", "default")
    copy_file(path_to_asset("images", "default.png"), "default")

from PyQt5 import Qt
from button import ButtonImage
from config import user, release, music_player
from assets.scripts.loggers import logger
from assets.scripts.auth_window import AuthWindow
from assets.scripts.profile_window import ProfileWindow
from assets.sprites.sprite import *
from building import init as BuilderInit
from button import Button, ButtonGroup
from level import LevelLoader
from ui import IngameUI
from assets.scripts.music_player import MusicPlayer


class CameraGroup(pygame.sprite.Group):
    def __init__(self, *sprites) -> None:
        super().__init__(*sprites)
        self.display_surface = pygame.display.get_surface()
        self.projection = None

        # Смещение камеры
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_width() // 2
        self.half_h = self.display_surface.get_height() // 2

    def project_building(self, building):
        if self.projection:
            self.remove(self.projection)
            self.projection = None
        cursor_pos = pygame.mouse.get_pos() + self.offset
        building.rect = building.image.get_rect(topleft=(cursor_pos[0] // 32 * 32, cursor_pos[1] // 32 * 32))
        self.projection = building
        self.add(building)

    def center_target_camera(self, target: pygame.sprite.Sprite) -> None:
        """Центрируем камеру на спрайте target и обновляем коорды проекции"""
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h
        if self.projection:
            # print(self.projection, len(self.sprites()))
            cursor_pos = pygame.mouse.get_pos() + self.offset
            self.projection.rect.topleft = cursor_pos[0] // 32 * 32, cursor_pos[1] // 32 * 32

    def custom_draw(self, centerfrom):
        self.center_target_camera(centerfrom)
        self.display_surface.fill(0)

        for sprite in sorted(self.sprites(), key=lambda x: x.display_layer):
            offsetPos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offsetPos)


class Game:
    FPS = 144

    def __init__(self, width, height) -> None:
        pygame.init()
        pygame.font.init()
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
        unscaled_bg = pygame.image.load(path_to_asset('images', 'MainMenuBg.jpg')).convert()
        bg = pygame.transform.scale(unscaled_bg, pygame.display.get_window_size())

        # Отрисовываем тексты
        small_font = pygame.font.Font(path_to_asset('fonts', 'CinnamonCoffeCake.ttf'), 20)
        font = pygame.font.Font(path_to_asset('fonts', 'CinnamonCoffeCake.ttf'), 35)
        big_font = pygame.font.Font(path_to_asset('fonts', 'CinnamonCoffeCake.ttf'), 100)
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
        music_player.play_bg_music('Waterfall.mp3', 3, 0.1)

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

    def play_screen(self):
        # Сбрасываем экран, загружаем карту и создаём персонажа
        self.screen.fill(0)
        LevelLoader.load(1)
        BUILDER = BuilderInit((3040, 3040), LevelLoader.ore_dict)
        Bullet.init()
        UI = IngameUI(self.screen.get_size())
        UI.initUI()
        UI.start_timer(90)

        player = Player((800, 640), LevelLoader.collision_rects)
        player_shadow = EntityShadow(player)

        # Создаём группу спрайтов, которая будет служить камерой
        camera_group = CameraGroup(LevelLoader.whole_map, player_shadow, player, BUILDER.building_sprite)
        bullet_group = pygame.sprite.Group()
        mob_group = pygame.sprite.Group()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if camera_group.projection:
                            # Отмена проекции здания
                            camera_group.remove(camera_group.projection)
                            camera_group.projection = None
                        else:
                            # Пауза игры
                            UI.pause_game()
                            self.clock.tick(999)  # Иначе следующий dt будет равен времени паузы.
                    elif event.key == pygame.K_b or event.key == pygame.K_TAB:
                        # Открытие/Закрытие UI стройки
                        # UI.building_panel.visible = not UI.building_panel.visible
                        # UI.viewport_panel.visible = not UI.viewport_panel.visible
                        if UI.building_panel.visible:
                            UI.building_panel.hide()
                            UI.viewport_panel.hide()
                        else:
                            UI.building_panel.show()
                            UI.viewport_panel.show()
                            UI.show_build_container('turret_container')
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                    obj_id = event.ui_object_id
                    hash_index = obj_id.rfind('#')
                    if obj_id.startswith('panel.#'):
                        # Кнопки категорий
                        building_type = obj_id[hash_index + 1:]
                        container = building_type.lower() + '_container'
                        UI.show_build_container(container)
                    elif obj_id.startswith('panel.scrolling_container.#'):
                        # Кнопки зданий внутри категорий
                        building_name = obj_id[hash_index + 1:].replace('_', ' ')
                        building = BUILDER.get_by_name(building_name)
                        camera_group.project_building(building)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        # Если здание выбрано к стройке и клик был не на UI
                        if camera_group.projection and not pygame.Rect(980, 0, 300, 720).contains(*event.pos, 1, 1):
                            # Если не пересекается с другими зданиями
                            if camera_group.projection.rect.collidelist(BUILDER.taken_territory) == -1:
                                # Если находится на земле
                                if not pygame.sprite.collide_mask(LevelLoader.ordered_level_sprites[2],
                                                                  camera_group.projection):
                                    # Если не за картой
                                    if pygame.Rect(0, 0, 3040, 3040).contains(camera_group.projection.rect):
                                        BUILDER.place(camera_group.projection)
                                        camera_group.remove(camera_group.projection)
                                        camera_group.projection = None
                        elif not pygame.Rect(980, 0, 300, 720).contains(*event.pos, 1, 1):
                            # Стрельба если лкм не обработан.
                            bullet = player.shoot()
                            bullet_group.add(bullet)
                            camera_group.add(bullet)

                UI.manager.process_events(event)

            # Обновляем местоположение игрока и его тень
            dt = self.clock.tick(self.FPS)
            player.update(dt)
            player_shadow.update()

            # Двигаем все выпущенные пули и проверяем коллизию
            bullet_group.update(dt / 1000)
            pygame.sprite.spritecollide(LevelLoader.ordered_level_sprites[2], bullet_group, True,
                                        pygame.sprite.collide_mask)

            # Отрисовка
            camera_group.custom_draw(centerfrom=player)
            UI.update_UI(dt)
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

    logging.config.fileConfig(fname=path_to_file("logging.conf"), disable_existing_loggers=False)
    if release:
        logging.disable(level=logging.WARNING)
    sys.excepthook = log_handler

    app = Qt.QApplication([])
    main_window = Game(1280, 720)
    main_window.run()
    app.exec()
