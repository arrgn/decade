import math
import sys

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pytmx.util_pygame import load_pygame

from assets.scripts.path_module import path_to_file
from assets.sprites.sprite import *
from button import Button, ButtonGroup
from ui import IngameUI


TILE_WIDTH = TILE_HEIGHT = 32
LEVEL_SIZE = (95 * TILE_WIDTH, 95 * TILE_HEIGHT)
SUN_POSITION = pygame.math.Vector2(7000, -5000)


class CameraGroup(pygame.sprite.Group):
    def __init__(self, *sprites) -> None:
        super().__init__(*sprites)
        self.display_surface = pygame.display.get_surface()

        # Смещение камеры
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_width() // 2
        self.half_h = self.display_surface.get_height() // 2

        # Всё для зума
        self.zoom_scale = 1
        self.internal_surf_size = (1280 * 1.4, 720 * 1.4)
        self.internal_surf = pygame.Surface(self.internal_surf_size, pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_rect(center=(self.half_w, self.half_h))
        self.internal_surf_size_vector = pygame.math.Vector2(self.internal_surf_size)
        self.internal_offset = pygame.math.Vector2()
        self.internal_offset.x = self.internal_surf_size[0] // 2 - self.half_w
        self.internal_offset.y = self.internal_surf_size[1] // 2 - self.half_h

    def center_target_camera(self, target: pygame.sprite.Sprite) -> None:
        """Центрируем камеру на спрайте target"""
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def custom_draw(self, player):
        self.center_target_camera(player)
        self.internal_surf.fill(0)

        for sprite in self.sprites():
            offsetPos = sprite.rect.topleft - self.offset + self.internal_offset
            self.internal_surf.blit(sprite.image, offsetPos)

        scaled_surf = pygame.transform.scale(self.internal_surf, self.internal_surf_size_vector * self.zoom_scale)
        scaled_rect = scaled_surf.get_rect(center=(self.half_w, self.half_h))

        self.display_surface.blit(scaled_surf, scaled_rect)


class Game:
    FPS = 144

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
        # Сбрасываем экран, загружаем карту и создаём персонажа
        self.screen.fill(0)
        pygame.display.update()

        UI = IngameUI(self.screen.get_size())
        tmx_data = load_pygame('assets/maps/Map.tmx')

        # Создаём словарь с tile'ами разных слоёв
        tiles = dict()
        border_tiles = list()
        for layerIndex, layer in enumerate(tmx_data.visible_layers):
            tiles[layerIndex] = list()
            if hasattr(layer, 'data'):  # Слой с плитками
                for x, y, surf in layer.tiles():
                    tile = Tile(layerIndex, (x * TILE_WIDTH, y * TILE_HEIGHT), surf)
                    if layer.name == 'Стены' and tmx_data.get_tile_properties(x, y, 2).get('class', None) == 'Препятствие':
                        border_tiles.append(tile.rect)
                    tiles[layerIndex].append(tile)
            else:  # Слой с объектами
                pass # NotImplemented, игнорированы

        
        # Создаём список со спрайтами слоёв
        all_map_sprites = list()
        for i, tile_set in tiles.items():
            layer_surf = pygame.Surface(LEVEL_SIZE, pygame.SRCALPHA)
            for tile in tile_set:
                layer_surf.blit(tile.image, tile.rect)
            layer_sprite = pygame.sprite.Sprite()
            if i == 0:
                layer_surf = layer_surf.convert()
            else:
                layer_surf = layer_surf.convert_alpha()
            layer_sprite.image = layer_surf
            layer_sprite.rect = pygame.Rect(0, 0, *LEVEL_SIZE)
            all_map_sprites.append(layer_sprite)

        # Выбираем спрайт теней и создаём от него тень
        wall_sprite = all_map_sprites[2]
        map_shadow = VectorShadow(wall_sprite, SUN_POSITION, height_multiplier=0.004)

        # В целях оптимизации лепим всё на 1 слой.
        whole_level = pygame.Surface(LEVEL_SIZE)
        for sprite in all_map_sprites[:2]:
            whole_level.blit(sprite.image, sprite.rect)
        whole_level.blit(map_shadow.image, map_shadow.rect)
        whole_sprite = pygame.sprite.Sprite()
        whole_sprite.image = whole_level.convert()
        whole_sprite.rect = whole_level.get_rect(topleft=(0, 0))

        # Инициализация интерфейса
        UI.initUI()
        UI.startTimer(90)

        player = Player((800, 640), border_tiles)
        player_shadow = EntityShadow(player)

        # Создаём группу спрайтов, которая будет служить камерой
        camera_group = CameraGroup(whole_sprite, player_shadow, wall_sprite, player)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEWHEEL:
                    camera_group.zoom_scale = max(min(camera_group.zoom_scale + event.y * 0.03, 0.73 * 2), 0.73)

                UI.manager.process_events(event)

            # Обновляем местоположение игрока и отрисовываем камеру в зависимости от него.
            dt = self.clock.tick(self.FPS)
            # self.screen.fill(0) убирает бесконечную стену и ставит чёрный бордер
            player.update(dt)
            player_shadow.update()
            t1 = time.perf_counter()
            camera_group.custom_draw(player)
            t2 = time.perf_counter()
            # print(f'{t2-t1=}')
            UI.updateUI(dt)
            pygame.display.update()


if __name__ == "__main__":
    main_window = Game(1280, 720)
    main_window.run()