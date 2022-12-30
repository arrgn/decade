import math
import sys

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pytmx.util_pygame import load_pygame

from assets.scripts.path_module import path_to_file
from button import Button, ButtonGroup
from ui import IngameUI

level_size = (95 * 32, 95 * 32)
 
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        image = pygame.image.load('assets/sprites/Character.png').convert_alpha()
        self.originalImage = pygame.transform.scale(image, (64, 64))
        self.image = self.originalImage.copy()
        self.rect = self.image.get_rect(topleft=pos)
        
        # Характеристики
        self.speed = 6
        self.health = 15
        self.is_moving = False

        # Вектор движения, вектор наклона
        self.direction = pygame.math.Vector2()
        self.rotation = pygame.math.Vector2(0, -1)

    def getInput(self):
        keys = pygame.key.get_pressed()

        # Ускорение на Shift
        if keys[pygame.K_LSHIFT]:
            self.speed = 12
        else:
            self.speed = 6
        
        # Проверка движения
        if keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0
        
        if keys[pygame.K_a]:
            self.direction.x = -1
        elif keys[pygame.K_d]:
            self.direction.x = 1
        else:
            self.direction.x = 0
    
    def getAngle(self):
        """Получить угол наклона в градусах из вектора наклона"""

        # Перед координатой Y стоит унарный минус потому что координаты
        # в pygame работают по уё.. другому.
        return math.degrees(math.atan2(self.rotation.x, -self.rotation.y))

    def tweenRotation(self):
        """Что-то типо 'анимации' вектора наклона в сторону вектора движения"""
        self.rotation = self.rotation.lerp(self.direction, 0.09)

    def update(self, border) -> None:
        self.getInput()

        if self.direction:
            self.is_moving = True

            # Наклон спрайта (Изменить вектор наклона, получить угол, повернуть изображение, поставить на прошлое место)
            self.tweenRotation()
            newDegree = -self.getAngle()
            self.image = pygame.transform.rotate(self.originalImage, newDegree)
            self.rect = self.image.get_rect(center=self.rect.center)

            # Движение (Тут всё понятно)
            self.direction.normalize_ip()
            newPos = self.rect.center + self.direction * self.speed
            for rect in border:
                if rect.collidepoint(newPos):
                    return False
            self.rect.center = newPos
        else:
            self.is_moving = False


class Tile(pygame.sprite.Sprite):
    def __init__(self, layer, pos, surf, *groups):
        super().__init__(*groups)
        self.image = surf
        self.rect = surf.get_rect(topleft=pos)
        self.layer = layer


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
        self.internal_surf_size = (2500, 2500)
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


class EntityShadow(pygame.sprite.Sprite):
    def __init__(self, sprite, *groups) -> None:
        super().__init__(*groups)
        self.offset_vector = pygame.math.Vector2(25, 25)
        self.connected_sprite = sprite
        self.update_shadow(force=True)

    def update_shadow(self, force=False):
        if self.connected_sprite.is_moving or force:
            mask = pygame.mask.from_surface(self.connected_sprite.image)
            mask_polygon = mask.outline()
            surface = pygame.Surface(mask.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(surface, (0, 0, 0, 128), mask_polygon)
            self.image = surface
            self.rect = surface.get_rect(center=self.connected_sprite.rect.center + self.offset_vector)

    def update(self) -> None:
        self.update_shadow()


class Game:
    FPS = 250

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
        UI = IngameUI(self.screen.get_size())
        tmx_data = load_pygame('assets/maps/Map.tmx')
        player = Player((800, 640))
        player_shadow = EntityShadow(player)

        # Создаём список всех Tile'ов и список стен для коллизий игрока.
        tiles = list()
        border_tiles = list()
        for layer in tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                    tile = Tile(layer.name, (x * 32, y * 32), surf)
                    if layer.name == 'Стены' and tmx_data.get_tile_properties(x, y, 2).get('class', None) == 'Препятствие':
                        border_tiles.append(tile.rect)
                    tiles.append(tile)

        ground_surface = pygame.Surface(level_size)
        for tile in tiles:
            ground_surface.blit(tile.image, tile.rect)

        ground_sprite = pygame.sprite.Sprite()
        ground_sprite.image = ground_surface
        ground_sprite.rect = ground_surface.get_rect()

        # Инициализация интерфейса
        UI.initUI()
        UI.startTimer(15)

        # Создаём группу спрайтов, которая будет служить камерой
        camera_group = CameraGroup(ground_sprite, player_shadow, player)
        print(camera_group.sprites())
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEWHEEL:
                    camera_group.zoom_scale = max(min(camera_group.zoom_scale + event.y * 0.03, 1.09), 0.52)

                UI.manager.process_events(event)
            # Обновляем местоположение игрока и отрисовываем камеру в зависимости от него.
            dt = self.clock.tick(self.FPS)
            # self.screen.fill(0) убирает бесконечную стену и ставит чёрный бордер
            player.update(border_tiles)
            player_shadow.update_shadow()
            camera_group.custom_draw(player)
            UI.updateUI(dt)
            pygame.display.update()


if __name__ == "__main__":
    main_window = Game(1280, 720)
    main_window.run()