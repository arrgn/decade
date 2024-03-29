import pygame
from assets.scripts.ui.sprite import Harvester, Wall, Conveyor, Turret
import copy
import os.path

TILE_WIDTH = TILE_HEIGHT = 64

class StructureGroup:
    def __init__(self) -> None:
        self.sprites = list()

    def __contains__(self, key):
        return key in self.sprites

    def __len__(self):
        return len(self.sprites)

    def remove(self, sprite):
        self.sprites.remove(sprite)

    def add(self, sprite):
        self.sprites.append(sprite)

    def update(self, dt, *args):
        for sprite in self.sprites:
            sprite.update(dt, *args)


def init(level_size, ore_dict, base_pos):
    # Загружаем spritesheet с 1x1 зданиями
    pass

    # Загружаем spritesheet с 2x2 зданиями
    spriteSheet = pygame.image.load(os.path.join('assets', 'maps', '2x2Buildings.png')).convert_alpha()
    x_size, y_size = map(lambda x: x // TILE_WIDTH, spriteSheet.get_size())
    spriteSheetData = [[[] for _ in range(y_size)] for _ in range(x_size)]
    spriteSheetData[0][0] = ('Copper drill', 'Harvester', 50)
    spriteSheetData[0][1] = ('Hematite drill', 'Harvester', 70)
    spriteSheetData[0][2] = ('Titan drill', 'Harvester', 100)
    spriteSheetData[0][3] = ('Copper wall', 'Wall', 200)
    spriteSheetData[0][4] = ('Titan wall', 'Wall', 400)
    spriteSheetData[0][5] = ('Hematite wall', 'Wall', 300)
    spriteSheetData[0][6] = ('Emerald wall', 'Wall', 500)
    spriteSheetData[1][0] = ('Conveyor', 'Conveyor', 50)
    spriteSheetData[1][1] = ('Emerald turret', 'Turret', 100)

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

        # Группы с апдейтами
        harvester_group = StructureGroup()
        conveyers_group = StructureGroup()
        turret_group = StructureGroup()

        conveyors_to_looks = dict()  # Used by conveyors in self with "rects_to_conveyors"
        rects_to_conveyors = dict()  # Used by harvesters

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
        def update(cls, dt, mobs=None):
            cls.harvester_group.update(dt / 1000)
            cls.conveyers_group.update(dt / 1000, cls.rects_to_conveyors, base_pos)
            cls.turret_group.update(dt, mobs)

        @classmethod
        def lock(cls):
            if not cls.locked:
                cls.locked = True
                cls.build_registry = tuple(cls.build_registry)

        @classmethod
        def delete_build_on_click(cls, point):
            for build in cls.built_buildings:
                if build.rect.collidepoint(point):
                    cls.built_buildings.remove(build)
                    cls.taken_territory.remove(build.rect)

                    cleared_surf = pygame.Surface((64, 64), pygame.SRCALPHA)
                    cleared_surf.fill((255, 255, 255, 255))
                    
                    cls.buildings_surface.fill((0, 0, 0, 0), build)
                    cls.building_sprite.image = cls.buildings_surface

                    is_conveyor = False
                    if tuple(build.rect) in cls.rects_to_conveyors:
                        is_conveyor = True
                        del cls.rects_to_conveyors[tuple(build.rect)]
                    if build in cls.conveyors_to_looks:
                        del cls.conveyors_to_looks[build]
                    if is_conveyor:
                        for harvester in cls.harvester_group.sprites:
                            harvester.update_conveyor_info(cls.rects_to_conveyors)
                    elif build.type == 'Turret':
                        cls.turret_group.remove(build)

                    if build in cls.harvester_group:
                        cls.harvester_group.remove(build)
                    elif build in cls.conveyers_group:
                        cls.conveyers_group.remove(build)

                    return True
            else:
                print("COULDN'T FIND ANYTHING")

        @classmethod
        def get_by_name(cls, name):
            for build in cls.build_registry:
                if build.name == name:
                    return copy.copy(build)
            return None

        @classmethod
        def place(cls, building):
            cls.buildings_surface.blit(building.image, building.rect)

            # Здесь нужно будет создать и объединить с тенью
            #

            if building.type == 'Harvester':
                maximum = 0
                resource = None
                for key, rects in ore_dict.items():
                    amount = len(building.rect.collidelistall(rects))
                    if amount > maximum:
                        resource = key
                        maximum = amount
                building.resource = resource
                building.harvest_rate = round(maximum / 2)
                building.update_conveyor_info(cls.rects_to_conveyors)
                cls.harvester_group.add(building)
            elif building.type == 'Conveyor':
                angle = getattr(building, 'rotated_by', None)
                
                offset_Rect = building.rect.copy()
                if angle == 270: # right
                    print('right chosen!')
                    offset_Rect.left += 64
                elif angle == 180: # bottom
                    print('bottom chosen!')
                    offset_Rect.top += 64
                elif angle == 90: # left
                    print('left chosen!')
                    offset_Rect.left -= 64
                else:
                    print('top chosen!')
                    offset_Rect.top -= 64
                building.looking_at = offset_Rect

                cls.conveyors_to_looks[building] = building.looking_at
                cls.rects_to_conveyors[tuple(building.rect)] = building
                cls.conveyers_group.add(building)

                for sprite in cls.harvester_group.sprites:
                    sprite.update_conveyor_info(cls.rects_to_conveyors)
            elif building.type == 'Turret':
                cls.turret_group.add(building)

            cls.building_sprite.image = cls.buildings_surface
            cls.built_buildings.append(building)
            cls.taken_territory.append(building.rect)


    for yi, y in enumerate(range(0, spriteSheet.get_height(), TILE_HEIGHT)):
        for xi, x in enumerate(range(0, spriteSheet.get_width(), TILE_WIDTH)):
            building_data = spriteSheetData[xi][yi]
            if building_data:
                name, building_type, health = building_data

                surface = pygame.Surface((TILE_WIDTH, TILE_HEIGHT)).convert()
                surface.blit(spriteSheet, (0, 0), area=(y, x, TILE_WIDTH, TILE_HEIGHT))

                structure = None
                if building_type == 'Harvester':
                    structure = Harvester(name, surface, health, None, power=0)
                elif building_type == 'Wall':
                    structure = Wall(name, surface, health)
                elif building_type == 'Conveyor':
                    structure = Conveyor(name, surface, health)
                elif building_type == 'Turret':
                    structure = Turret(name, surface, health)

                BuildManager.append(structure)
    
    BuildManager.lock()
    return BuildManager