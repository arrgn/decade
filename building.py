import pygame
from dataclasses import dataclass
import os.path

TILE_WIDTH = TILE_HEIGHT = 64


def init(level_size):
    # Загружаем spritesheet с 1x1 зданиями
    pass

    # Загружаем spritesheet с 2x2 зданиями
    spriteSheet = pygame.image.load(os.path.join('assets', 'maps', '2x2Buildings.png')).convert_alpha()
    x_size, y_size = map(lambda x: x // TILE_WIDTH, spriteSheet.get_size())
    spriteSheetData = [[[] for _ in range(y_size)] for _ in range(x_size)]
    spriteSheetData[0][0] = ('Copper drill', 'Drill')
    spriteSheetData[0][1] = ('Hematite drill', 'Drill')
    spriteSheetData[0][2] = ('Titan drill', 'Drill')
    spriteSheetData[0][3] = ('Copper wall', 'Wall')
    spriteSheetData[0][4] = ('Titan wall', 'Wall')

    # Загружаем spritesheet с 3x3 зданиями
    pass

    class BuildManager:
        building_sprite = pygame.sprite.Sprite()

        # Поверхности зданий и их теней
        buildings_surface = pygame.Surface(level_size, pygame.SRCALPHA)
        shadow_surface = pygame.Surface(level_size, pygame.SRCALPHA)

        # Аттрибуты. Т.к спрайт не наследованный.
        building_sprite.display_layer = 2
        building_sprite.image = buildings_surface
        building_sprite.rect = pygame.Rect(0, 0, *level_size)

        # Данные об уровне
        build_registry = list()
        built_buildings = list()
        taken_territory = list()
        locked = False

        @classmethod
        def append(cls, build):
            if cls.locked:
                raise PermissionError('Build manager is already initialized')
            cls.build_registry.append(build)
        
        @classmethod
        def lock(cls):
            if not cls.locked:
                cls.locked = True
                cls.build_registry = tuple(cls.build_registry)

        @classmethod
        def get_by_name(cls, name):
            for build in cls.build_registry:
                if build.name == name:
                    return build
            return None

        @classmethod
        def place(cls, building):
            cls.buildings_surface.blit(building.image, building.rect)

            # Здесь нужно будет создать и объединить с тенью
            #

            cls.building_sprite.image = cls.buildings_surface
            cls.built_buildings.append(building)
            cls.taken_territory.append(building.rect)


    @dataclass(init=False, unsafe_hash=True)
    class Building(pygame.sprite.Sprite):
        def __init__(self, name, building_type, image, *groups) -> None:
            super().__init__(*groups)
            self.name = name
            self.type = building_type
            self.image = image
            self.display_layer = 2
            self.manager = BuildManager

        def project_to_screen(self, screen: pygame.Surface, abs_cursor_pos):
            """abs_cursor_pos - Координаты курсора на экране + offset камеры"""
            x, y = abs_cursor_pos[0] // 32 * 32, abs_cursor_pos[1] // 32 * 32
            screen.blit(self.texture, (x, y))

        def place(self, abs_cursor_pos):
            """abs_cursor_pos - Координаты курсора на экране + offset камеры"""
            x, y = abs_cursor_pos[0] // 32 * 32, abs_cursor_pos[1] // 32 * 32
            self.manager.built_buildings.append((self, (x, y)))


    for yi, y in enumerate(range(0, spriteSheet.get_height(), TILE_HEIGHT)):
        for xi, x in enumerate(range(0, spriteSheet.get_width(), TILE_WIDTH)):
            building_data = spriteSheetData[xi][yi]
            if building_data:
                name, building_type = building_data

                surface = pygame.Surface((TILE_WIDTH, TILE_HEIGHT)).convert()
                surface.blit(spriteSheet, (0, 0), area=(y, x, TILE_WIDTH, TILE_HEIGHT))
                BuildManager.append(Building(name, building_type, surface))
    
    BuildManager.lock()
    return BuildManager