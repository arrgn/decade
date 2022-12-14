import pygame

from pytmx.util_pygame import load_pygame
from assets.sprites.sprite import Tile, VectorShadow
from assets.scripts.path_module import path_to_asset


class LevelLoader:
    levels = {
        "LEVEL 1": {
            'TILE_WIDTH': 32,
            'TILE_HEIGHT': 32,
            'LEVEL_SIZE': (95 * 32, 95 * 32),
            'SUN_POSITION': pygame.math.Vector2(-7000, -5000),
            'DESCRIPTION': 'First level',
            'DATE': '12.01.2023',
            'FILE_NAME': "Map.tmx",

            'BASE_LOCATION': pygame.Rect(1312, 2560, 64, 64),
            'WAVES': {
                1: 5,
                2: 10,
                3: 13,
                4: 15,
                5: 18,
                6: 20,
                7: 21,
                8: 40
            }
        },

        "LEVEL 2": {
            'TILE_WIDTH': 32,
            'TILE_HEIGHT': 32,
            'LEVEL_SIZE': (50 * 32, 50 * 32),
            'SUN_POSITION': pygame.math.Vector2(-7000, -5000),
            'DESCRIPTION': 'Second level',
            'DATE': '12.01.2023',
            'FILE_NAME': "Map2.tmx",

            'BASE_LOCATION': pygame.Rect(1312, 2560, 64, 64),
            'WAVES': {

            }
        },

        "LEVEL 3": {
            'TILE_WIDTH': 32,
            'TILE_HEIGHT': 32,
            'LEVEL_SIZE': (95 * 32, 95 * 32),
            'SUN_POSITION': pygame.math.Vector2(-7000, -5000),
            'DESCRIPTION': 'Third level',
            'DATE': '12.01.2023',
            'FILE_NAME': "Map3.tmx",

            'BASE_LOCATION': pygame.Rect(1312, 2560, 64, 64),
            'WAVES': {

            }
        }
    }

    ordered_level_sprites = list()  # Спрайты по слоям
    collision_rects = list()  # Коллизия для игрока
    whole_map = None  # Идёт на рендер (1 спрайт на всю карту)

    @classmethod
    def load(cls, level: str):
        """
            Вызывать только с инициализованным pygame.display
            @param level имя файла с картой
        """
        # Создаём словарь с tile'ами разных слоёв
        tmx_data = load_pygame(path_to_asset("maps", cls.levels[level]["FILE_NAME"]))

        tiles = dict()
        border_tiles = list()
        ore_dict = {
            'Titan': list(),
            'Copper': list(),
            'Hematite': list(),
            'Coal': list(),
            'Emerald': list()
        }

        for layerIndex, layer in enumerate(tmx_data.visible_layers):
            tiles[layerIndex] = list()
            if hasattr(layer, 'data'):  # Слой с плитками
                for x, y, surf in layer.tiles():
                    tile = Tile(layerIndex, (x * cls.levels[level]['TILE_WIDTH'], y * cls.levels[level]['TILE_HEIGHT']),
                                surf)
                    if layer.name == 'Стены' and tmx_data.get_tile_properties(x, y, 2).get('class',
                                                                                           None) == 'Препятствие':
                        border_tiles.append(tile.rect)
                    elif layer.name == 'Руда':
                        ore_class = tmx_data.get_tile_properties(x, y, 1).get('class', None)
                        if ore_class and ore_class in ore_dict:
                            ore_dict[ore_class].append(
                                pygame.Rect(x * cls.levels[level]['TILE_WIDTH'], y * cls.levels[level]['TILE_HEIGHT'],
                                            32, 32))

                    tiles[layerIndex].append(tile)
            else:  # Слой с объектами
                pass  # NotImplemented, игнорированы

        # Создаём список со спрайтами слоёв
        all_map_sprites = list()
        for i, tile_set in tiles.items():
            layer_surf = pygame.Surface(cls.levels[level]['LEVEL_SIZE'], pygame.SRCALPHA)
            for tile in tile_set:
                layer_surf.blit(tile.image, tile.rect)
            layer_sprite = pygame.sprite.Sprite()
            if i == 0:
                layer_surf = layer_surf.convert()
            else:
                layer_surf = layer_surf.convert_alpha()
            layer_sprite.image = layer_surf
            layer_sprite.rect = pygame.Rect(0, 0, *cls.levels[level]['LEVEL_SIZE'])
            all_map_sprites.append(layer_sprite)

        # Выбираем спрайт теней и создаём от него тень
        wall_sprite = all_map_sprites[2]
        all_map_sprites[2].mask = pygame.mask.from_surface(wall_sprite.image)
        map_shadow = VectorShadow(wall_sprite, cls.levels[level]['SUN_POSITION'], height_multiplier=0.004)

        # В целях оптимизации лепим всё на 1 слой.
        whole_level = pygame.Surface(cls.levels[level]['LEVEL_SIZE'])
        for sprite in all_map_sprites[:2]:
            whole_level.blit(sprite.image, sprite.rect)
        whole_level.blit(map_shadow.image, map_shadow.rect)
        whole_level.blit(wall_sprite.image, wall_sprite.rect)
        whole_sprite = pygame.sprite.Sprite()
        whole_sprite.image = whole_level.convert()
        whole_sprite.rect = whole_level.get_rect(topleft=(0, 0))
        whole_sprite.display_layer = 1

        cls.ordered_level_sprites = all_map_sprites
        cls.collision_rects = border_tiles
        cls.whole_map = whole_sprite
        cls.ore_dict = ore_dict

        return cls.levels[level]['BASE_LOCATION']
