import logging.config
import sys
import traceback
import typing

import pygame.event
import pygame_gui
import random
import json

from assets.scripts.QT.permissions import PermissionWindow
from assets.scripts.path_module import create_dir, copy_user_file, path_to_asset, path_to_file, path_to_userdata, \
    copy_file

if __name__ == "__main__":
    """
        Прикол в том, что при создании юзера мы копируем дефолтные файлы из папки userdata/default.
        Если разместить этот код после импорта юзера/окна авторизации - вылезет ошибка, так как юзер не сможет
        копировать файлы либо окно авторизации не сможет открыть  файл.
        В этом месте лучше копировать все необходимые файлы по умолчанию для юзера.
    """
    create_dir("userdata", "default")
    copy_user_file(path_to_asset("images", "default.png"), "default")

from os.path import basename
from PyQt5.QtWidgets import QFileDialog, QApplication
from pygame_textinput import TextInputVisualizer
from assets.scripts.configuration.config import release, music_player, user, path_to_maps_config, config
from assets.scripts.configuration.loggers import logger
from assets.scripts.ui.sprite import *
from assets.scripts.instances.events import *
from assets.scripts.ui.building import init as BuilderInit
from assets.scripts.ui.button import Button, ButtonGroup
from assets.scripts.level import LevelLoader
from assets.scripts.ui.ui import IngameUI
from assets.scripts.profile_group import ProfileGroup
from assets.scripts.instances.fonts import *
from assets.scripts.instances.functions import save_and_exit
from assets.scripts.ui.scroll_area import ScrollArea
from assets.scripts.QT.map_form import FormWindow


class MobGroup(pygame.sprite.Group):
    total_killed = 0

    def __init__(self, spawn_rect, waypoints, camera_group, *sprites) -> None:
        super().__init__(*sprites)
        self.spawn_rect = spawn_rect
        self.waypoints = waypoints
        self.camera_group = camera_group

    def start_wave(self, amount, force=False):
        if not self.sprites() or force:
            while amount > 0:
                rand_x = random.randint(self.spawn_rect.x, self.spawn_rect.x + self.spawn_rect.width)
                rand_y = random.randint(self.spawn_rect.y, self.spawn_rect.y + self.spawn_rect.height)

                en = Enemy((rand_x, rand_y), self, self.camera_group)
                off = [(w[0] + random.randint(-20, 20), w[1] + random.randint(-20, 20)) for w in self.waypoints]

                en.update_walk(*off)

                amount -= 1
        else:
            print('ВОЛНА НЕ ЗАКОНЧЕНА. НЕЛЬЗЯ НАЧАТЬ НОВУЮ')


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
        building.rect = building.image.get_rect(topleft=(cursor_pos[0] // 64 * 64, cursor_pos[1] // 64 * 64))
        self.projection = building
        self.add(building)

    def center_target_camera(self, target: pygame.sprite.Sprite) -> None:
        """Центрируем камеру на спрайте target и обновляем коорды проекции"""
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h
        if self.projection:
            cursor_pos = pygame.mouse.get_pos() + self.offset
            self.projection.rect.topleft = cursor_pos[0] // 64 * 64 - 32, cursor_pos[1] // 64 * 64

    def custom_draw(self, centerfrom):
        self.center_target_camera(centerfrom)
        self.display_surface.fill(0)

        for sprite in sorted(self.sprites(), key=lambda x: x.display_layer):
            offsetPos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offsetPos)


class Game:
    FPS = config.FPS

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption('Decade')
        if config.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(config.size)
        self.clock = pygame.time.Clock()
        self.profile_group = ProfileGroup(self.screen.get_rect().topright, 60, 35, 10)
        pygame.display.update()

        # Запускаем музочку.
        music_player.play_bg_music('Waterfall.mp3', 3, 0.1)

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_and_exit()

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
        game_title = big_font.render(config["title"], True, '#E1FAF9')
        version_title = small_font.render(config["version"], True, '#E1FAF9')

        # Создаём кнопки и добавляем их в группу
        play_button = Button((50, 200, 200, 50), 'Play', font, 'White', '#0496FF', '#006BA6')
        options_button = Button((50, 275, 200, 50), 'Options', font, 'White', '#0496FF', '#006BA6')
        exit_button = Button((50, 350, 200, 50), 'Exit', font, 'White', '#0496FF', '#006BA6')
        menu_buttons = ButtonGroup(play_button, options_button, exit_button)

        # Main loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_and_exit()

                elif event.type == pygame.MOUSEMOTION:
                    menu_buttons.check_hover(event.pos)
                    self.profile_group.check_hover(event.pos)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Проверяем, нажата ли левая кнопка мыши, и находится ли курсор над кнопкой.
                    if event.button == pygame.BUTTON_LEFT:
                        clicked_button = menu_buttons.check_click(event.pos)
                        if clicked_button is None:
                            self.profile_group.check_click(event.pos)

                        if clicked_button is play_button:
                            self.map_management(user.get_maps)
                        elif clicked_button is options_button:
                            self.settings_screen()
                        elif clicked_button is exit_button:
                            save_and_exit()

            # Отрисовываем всё по порядку
            self.screen.blit(bg, (0, 0))
            pygame.draw.rect(self.screen, '#EE6C4D', game_title.get_rect(topleft=(50, 20)))
            self.screen.blit(game_title, (50, 20))
            self.screen.blit(version_title, version_title.get_rect(bottomright=(pygame.display.get_window_size())))
            menu_buttons.update(self.screen)
            self.profile_group.show(self.screen)

            self.clock.tick(self.FPS)
            pygame.display.update()

    def map_management(self, get_maps):
        # Масштабируем задний фон под размеры окна
        unscaled_bg = pygame.image.load(path_to_asset('images', 'MainMenuBg.jpg')).convert()
        bg = pygame.transform.scale(unscaled_bg, pygame.display.get_window_size())

        # Отрисовываем тексты
        game_title = big_font.render(config["title"], True, '#E1FAF9')
        version_title = small_font.render(config["title"], True, '#E1FAF9')
        hint = small_font.render("Use Key-Up/Key-Down to scroll", True, "#E1FAF9")

        # Создаем скроллер
        scroll = ScrollArea((50, 200, 675, 400), 100, 5, 128, (0, 0, 0), get_maps, self.play_screen)

        # Создаём кнопки и добавляем их в группу
        back_button = Button((50, self.screen.get_height() - 70, 200, 50), "Back", font, 'White', '#0496FF', '#006BA6')
        add_map_button = Button((scroll.rect.topright[0] + 20, scroll.rect.topright[1], 220, 50), "Add map w/JSON",
                                font, 'White', '#0496FF', '#006BA6')
        add_map_with_form = Button((add_map_button.rect.bottomleft[0], add_map_button.rect.bottomleft[1] + 20, 220, 50),
                                   'Add map via Form', font, 'White', '#0496FF', '#006BA6')
        manage_access_button = Button(
            (add_map_with_form.rect.bottomleft[0], add_map_with_form.rect.bottomleft[1] + 20, 220, 50), "Manage access",
            font, 'White', '#0496FF', '#006BA6')
        menu_buttons = ButtonGroup(back_button, add_map_button, add_map_with_form, manage_access_button)

        def add_map_data(info: typing.Dict[str, typing.Any]):
            with open(path_to_maps_config, mode="r+") as maps_file:
                maps = json.load(maps_file)
                for k, v in info.items():
                    copy_file(v["FILE_NAME"], ["assets", "maps"])  # Save map in userdata
                    user.add_map(k, v["DESCRIPTION"], v["ACCESS"], v["DATE"])
                    v["FILE_NAME"] = basename(v["FILE_NAME"])
                    maps[k] = v
                maps_file.seek(0)
                json.dump(maps, maps_file, indent=2)
                maps_file.truncate()

        def change_access(new: list[list[str, bool]], old: list[list[str, bool]], map_: str):
            for i in range(len(new)):
                if new[i] != old[i]:
                    if new[i][1]:
                        user.give_access_to_map(new[i][0], map_, "USER")
                    else:
                        user.take_away_access_to_map(new[i][0], map_)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_and_exit()

                elif event.type == pygame.MOUSEMOTION:
                    menu_buttons.check_hover(event.pos)
                    self.profile_group.check_hover(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        clicked_button = menu_buttons.check_click(pygame.mouse.get_pos())
                        if clicked_button is None:
                            if self.profile_group.check_click(pygame.mouse.get_pos()):
                                scroll.check_click(pygame.mouse.get_pos())
                            else:
                                scroll.reload_content()

                        if clicked_button is back_button:
                            return

                        elif clicked_button is add_map_button:
                            filepath = QFileDialog.getOpenFileName(None, "Open file",
                                                                   path_to_userdata("", str(user.get_user_id())),
                                                                   "Map metadata (*.json)")[0]
                            if not filepath == "":
                                with open(filepath) as file:
                                    data = json.load(file)
                                    add_map_data(data)
                            else:
                                logger.warning("Got null filename")
                            scroll.reload_content()

                        elif clicked_button is add_map_with_form:
                            window = FormWindow()
                            window.show()
                            window.map_added.connect(add_map_data)

                        elif clicked_button is manage_access_button:
                            map_name = "The Cave of the Devotee"
                            data = list(map(lambda x: [x[0], x[1] is not None], user.get_users_with_access(map_name)))
                            window = PermissionWindow(user.get_owned_maps(), data)
                            window.show()
                            window.permission_changed.connect(lambda x, y: change_access(x, data, y))

                elif event.type == pygame.MOUSEWHEEL:
                    scroll.scroll(-event.y)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        print('scrolling up')
                        scroll.scroll(-3)
                    elif event.key == pygame.K_DOWN:
                        print('scrolling down')
                        scroll.scroll(3)

            # Отрисовываем всё по порядку
            self.screen.blit(bg, (0, 0))
            pygame.draw.rect(self.screen, '#EE6C4D', game_title.get_rect(topleft=(50, 20)))
            pygame.draw.rect(self.screen, '#EE6C4D', hint.get_rect(topleft=(60 + game_title.get_width(), 20)))
            self.screen.blit(game_title, (50, 20))
            self.screen.blit(version_title, version_title.get_rect(bottomright=(pygame.display.get_window_size())))
            self.screen.blit(hint, (60 + game_title.get_width(), 20))
            scroll.show(self.screen)
            menu_buttons.update(self.screen)
            self.profile_group.show(self.screen)

            self.clock.tick(self.FPS)
            pygame.display.update()

    def settings_screen(self):
        self.screen.fill(0)

        # Масштабируем задний фон под размеры окна
        unscaled_bg = pygame.image.load(path_to_asset('images', 'MainMenuBg.jpg')).convert()
        bg = pygame.transform.scale(unscaled_bg, pygame.display.get_window_size())

        # Отрисовываем тексты
        game_title = big_font.render('Decade', True, '#E1FAF9')
        version_title = small_font.render('Version Prealpha 0.1', True, '#E1FAF9')
        volume = font.render("Volume", True, "#E1FAF9")

        # Создаём кнопки и добавляем их в группу
        back_button = Button((50, self.screen.get_height() - 70, 200, 50), "Back", font, 'White', '#0496FF', '#006BA6')
        accept_button = Button((back_button.rect.topright[0] + 50, back_button.rect.topright[1], 200, 50), "Accept",
                               font, "White", '#0496FF', '#006BA6')
        menu_buttons = ButtonGroup(back_button, accept_button)

        # Поля ввода
        sound_volume = TextInputVisualizer(font_object=font, antialias=True)
        sound_volume.value = str(music_player.mult * 100)

        run = True
        while run:
            events = pygame.event.get()

            sound_volume.update(events)

            for event in events:
                if event.type == pygame.QUIT:
                    save_and_exit()

                elif event.type == pygame.MOUSEMOTION:
                    menu_buttons.check_hover(event.pos)
                    self.profile_group.check_hover(event.pos)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    clicked_button = menu_buttons.check_click(event.pos)
                    if clicked_button is None:
                        self.profile_group.check_click(event.pos)

                    if clicked_button is back_button:
                        run = False
                        break
                    elif clicked_button is accept_button:
                        value = sound_volume.value
                        try:
                            value = float(value) / 100
                            if value < 0:
                                value = 0
                            elif value > 1:
                                value = 1
                            config.volume = value
                            music_player.set_global_volume(value)
                            sound_volume.value = str(value * 100)
                        except TypeError:
                            logger.exception("Tracked exception occurred")

            # Отрисовываем всё по порядку
            self.screen.blit(bg, (0, 0))
            pygame.draw.rect(self.screen, '#EE6C4D', game_title.get_rect(topleft=(50, 20)))
            pygame.draw.rect(self.screen, "#EE6C4D", sound_volume.surface.get_rect(
                topleft=(60 + volume.get_width(), 30 + game_title.get_height())))
            pygame.draw.rect(self.screen, "#EE6C4D", volume.get_rect(topleft=(50, 30 + game_title.get_height())))
            self.screen.blit(game_title, (50, 20))
            self.screen.blit(version_title, version_title.get_rect(bottomright=(pygame.display.get_window_size())))
            self.screen.blit(sound_volume.surface, (60 + volume.get_width(), 30 + game_title.get_height()))
            self.screen.blit(volume, (50, 30 + game_title.get_height()))
            menu_buttons.update(self.screen)
            self.profile_group.show(self.screen)

            self.clock.tick(self.FPS)
            pygame.display.update()

    def play_screen(self, map_name):
        # Сбрасываем экран, загружаем карту и создаём персонажа
        self.screen.fill(0)
        base_rect, waypoints, spawn_rect, wave_info, timer_break = LevelLoader.load(map_name)
        base = PlayerBase.getInstance()
        base.rect = base_rect
        BUILDER = BuilderInit((3040, 3040), LevelLoader.ore_dict, base_rect)

        Bullet.init()

        UI = IngameUI(self.screen.get_size(), map_name, wave_info, timer_break)
        UI.initUI()
        UI.start_timer(timer_break)

        setattr(base, 'UI', UI)

        player = Player((800, 640), LevelLoader.collision_rects)
        player_shadow = EntityShadow(player)

        # Создаём группу спрайтов, которая будет служить камерой
        camera_group = CameraGroup(LevelLoader.whole_map, base, player_shadow, player, BUILDER.building_sprite)
        bullet_group = pygame.sprite.Group()
        mob_group = MobGroup(spawn_rect, waypoints, camera_group)
        Turret.set_groups(bullet_group, camera_group)

        def place_building_if_can():
            # Если здание выбрано к стройке и клик был не на UI
            if camera_group.projection and not pygame.Rect(980, 0, 300, 720).contains(*event.pos, 1, 1):
                # Если не пересекается с другими зданиями
                if camera_group.projection.rect.collidelist(BUILDER.taken_territory) == -1:
                    # Если находится на земле
                    if not pygame.sprite.collide_mask(LevelLoader.ordered_level_sprites[2], camera_group.projection):
                        # Если не за картой
                        if pygame.Rect(0, 0, 3040, 3040).contains(
                                camera_group.projection.rect):  # TODO, подогнать под размеры карты.

                            BUILDER.place(camera_group.projection)
                            camera_group.remove(camera_group.projection)

                            camera_group.projection = None
                            return True

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_and_exit()
                elif event == SAVE_AND_RETURN:
                    base = None
                    UI = None
                    BUILDER = None
                    PlayerBase.instance = None
                    return
                elif event.type == pygame.MOUSEWHEEL:
                    if camera_group.projection:
                        if event.y > 0:
                            camera_group.projection.rotate_right()
                        else:
                            camera_group.projection.rotate_left()
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
                        # UI.viewport_panel.visible =  UI.viewport_panel.visible
                        if UI.building_panel.visible:
                            UI.building_panel.hide()
                            UI.viewport_panel.hide()
                        else:
                            UI.building_panel.show()
                            UI.viewport_panel.show()
                            UI.show_build_container('turret_container')
                    elif event.key == pygame.K_r and camera_group.projection:
                        camera_group.projection.rotate_right()
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
                        if not building:
                            print(f"NO INFORMATION ABOUT {building_name}")
                        else:
                            # building.image = pygame.transform.rotate(building.image, placement_angle)
                            camera_group.project_building(building)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        if place_building_if_can():
                            pass
                        elif not pygame.Rect(980, 0, 300, 720).contains(*event.pos, 1, 1):
                            # Стрельба если здание не построилось
                            bullet = player.shoot()
                            bullet_group.add(bullet)
                            camera_group.add(bullet)
                    elif event.button == pygame.BUTTON_RIGHT:
                        state = place_building_if_can()
                        if state:
                            times = building.angle % 360
                            building = BUILDER.get_by_name(building.name)

                            for i in range(times // 90):
                                building.rotate_left()

                            camera_group.project_building(building)
                        else:
                            BUILDER.delete_build_on_click(event.pos + camera_group.offset)
                elif event == GAME_ENDED:
                    score = UI.end_game(mob_group.total_killed)
                    user.save_score(map_name, score)
                    print('DA SCORE IS', score)
                    return
                elif event == WAVE_CLEARED:
                    pass
                elif event == WAVE_STARTS:
                    mob_group.start_wave(event.amount)
                elif event == MOB_KILLED:
                    mob_group.total_killed += 1

                UI.manager.process_events(event)

            # Обновляем местоположение игрока и его тень
            dt = self.clock.tick(self.FPS)
            player.update(dt)
            player_shadow.update()

            BUILDER.update(dt, mob_group)

            # Двигаем все выпущенные пули и проверяем коллизию
            bullet_group.update(dt / 1000)
            mob_group.update(dt)
            pygame.sprite.spritecollide(LevelLoader.ordered_level_sprites[2], bullet_group, True,
                                        pygame.sprite.collide_mask)

            if base:
                collision = pygame.sprite.spritecollide(base, mob_group, False)
                if collision:
                    pygame.event.post(GAME_ENDED)

            collision = pygame.sprite.groupcollide(bullet_group, mob_group, True, False)
            if collision:
                enemy = tuple(collision.values())[0][0]
                enemy.take_damage(3)

            # Отрисовка
            camera_group.custom_draw(centerfrom=player)
            UI.update_UI(dt, len(mob_group.sprites()))  # OPTIMIZE
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

    app = QApplication([])
    main_window = Game()
    main_window.run()
    app.exec()
