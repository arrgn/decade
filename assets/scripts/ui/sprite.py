from __future__ import annotations
import math

import pygame
from os.path import join
from dataclasses import dataclass
from assets.scripts.instances.events import MOB_KILLED
from assets.scripts.path_module import path_to_asset
from pygame.sprite import Sprite, Group

TILE_WIDTH = TILE_HEIGHT = 32
LEVEL_WIDTH, LEVEL_HEIGHT = 95 * TILE_WIDTH, 95 * TILE_HEIGHT


class Structure(Sprite):
    def __init__(self, name, building_type, image, health, *groups) -> None:
        super().__init__(*groups)
        self.health = health
        self.name = name
        self.type = building_type
        self.image = image
        self.display_layer = 2
        self.angle = 0

    @property
    def rotated_by(self):
        return self.angle % 360

    def rotate_right(self):
        self.angle -= 90
        self.image = pygame.transform.rotate(self.image, -90)

    def rotate_left(self):
        self.angle += 90
        self.image = pygame.transform.rotate(self.image, 90)

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.kill()


class Harvester(Structure):
    def __init__(self, name, image, health, resource=None, power=4, *groups) -> None:
        super().__init__(name, 'Harvester', image, health, *groups)
        self.resource_timer = 0
        self.harvest_rate = round(power / 2)
        self.resource = resource
        self.nearby_conveyors = None
        self.holding = 0

    def update_conveyor_info(self, conveyer_dict):
        toprect = self.rect.copy().move(0, -64)
        bottomrect = self.rect.copy().move(0, 64)
        middleleftrect = self.rect.copy().move(-64, 0)
        middlerightrect = self.rect.copy().move(64, 0)

        available_convs = list()
        for i in (toprect, bottomrect, middleleftrect, middlerightrect):
            conv = conveyer_dict.get(tuple(i), None)
            if conv:
                available_convs.append(conv)

        self.nearby_conveyors = available_convs

    def update(self, dt) -> None:  # In secs
        self.resource_timer += dt
        if self.resource_timer > 2 and self.holding < 10:
            self.resource_timer = 0
            self.holding = min(10, self.holding + self.harvest_rate)
            print(self.resource, self.holding)

        if self.holding and self.nearby_conveyors:
            print('checking')
            for conv in self.nearby_conveyors:
                if not conv.holding_item or conv.holding_item[0] == self.resource:
                    conv.transfer_resource(self.resource, self.holding)
                    self.holding = 0
                    break


class PlayerBase(Structure):
    """Singleton"""
    instance = None

    def __init__(self, *groups) -> PlayerBase:
        if not self.__class__.instance:
            surf = pygame.Surface((64, 64)).convert()
            surf.blit(pygame.image.load(join('assets', 'maps', '2x2Buildings.png')), (0, 0), (448, 0, 64, 64))
            super().__init__("PlayerBase", 'Misc', surf, 2000)
            self.resources = dict.fromkeys(('Coal', 'Copper', 'Hematite', 'Titan', 'Emerald'), 0)
            self.UI = None
            self.__class__.instance = self
        else:
            return self.__class__.instance

    def transfer_resource(self, resource, amount):
        self.resources[resource] += amount
        self.UI.update_resource_amounts(self.resources)

    @classmethod
    def getInstance(cls):
        if not cls.instance:
            cls.instance = cls()
        return cls.instance


class Wall(Structure):
    def __init__(self, name, image, health, *groups) -> None:
        super().__init__(name, 'Wall', image, health, *groups)


class Conveyor(Structure):
    def __init__(self, name, image, health, *groups) -> None:
        super().__init__(name, 'Conveyor', image, health, *groups)
        self.holding_item = None
        self.looking_at: pygame.Rect

    def transfer_resource(self, resource, amount):
        if not self.holding_item:
            self.holding_item = (resource, amount)
        else:
            self.holding_item = self.holding_item[0], self.holding_item[1] + amount

    def update(self, dt, conveyer_dict, base_pos) -> None:
        if self.holding_item and self.looking_at:
            coords = tuple(self.looking_at)
            if coords in conveyer_dict:
                conveyor = conveyer_dict[coords]
                if not conveyor.holding_item or self.holding_item[0] == conveyor.holding_item[0]:
                    conveyor.transfer_resource(*self.holding_item)
                    self.holding_item = None
            elif coords == base_pos:
                PlayerBase.getInstance().transfer_resource(*self.holding_item)
                self.holding_item = None


class Bullet(Sprite):
    texture = None
    speed = 800
    display_layer = 5

    def __init__(self, pos, direction=None, *groups) -> None:
        super().__init__(*groups)
        if not direction:
            self.direction = pygame.math.Vector2(
                pygame.mouse.get_pos()) - (self.half_w, self.half_h)
        else:
            self.direction = direction

        self.direction.scale_to_length(1)
        rotate_angle = math.degrees(math.atan2(
            self.direction.x, self.direction.y))

        scaled_image = pygame.transform.scale(self.texture, (16, 32))
        self.image = pygame.transform.rotate(scaled_image, rotate_angle)
        self.rect = self.image.get_rect(center=pos)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt

    @classmethod
    def init(cls):
        cls.half_w, cls.half_h = map(
            lambda x: x // 2, pygame.display.get_surface().get_size())
        cls.texture = pygame.image.load(
            join('assets', 'sprites', 'BulletSprite.png')).convert_alpha()


class Player(Sprite):
    accelerated_speed = 900
    regular_speed = 500
    turning_speed = 5
    max_health = 15
    display_layer = 3

    def __init__(self, pos, collideables=None, *groups):
        super().__init__(*groups)
        image = pygame.image.load(
            join('assets', 'sprites', 'Character.png')).convert_alpha()
        self.originalImage = pygame.transform.scale(image, (64, 64))
        self.image = self.originalImage.copy()
        self.rect = self.image.get_rect(topleft=pos)

        # Характеристики
        self.collideables = collideables
        self.speed = self.regular_speed
        self.health = self.max_health
        self.is_moving = False

        # Вектор движения, вектор наклона
        self.direction = pygame.math.Vector2()
        self.rotation = pygame.math.Vector2(0, -1)

    def setCollisions(self, border: list[pygame.Rect]) -> None:
        self.collideables = border

    def getInput(self):
        keys = pygame.key.get_pressed()

        # Ускорение на Shift
        if keys[pygame.K_LSHIFT]:
            self.speed = self.accelerated_speed
        else:
            self.speed = self.regular_speed

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

    def shoot(self):
        return Bullet(self.rect.center)

    def getAngle(self):
        """Получить угол наклона в градусах из вектора наклона"""

        # Перед координатой Y стоит унарный минус потому что координаты
        # в pygame работают по уё.. другому.
        return math.degrees(math.atan2(self.rotation.x, -self.rotation.y))

    def tweenRotation(self, dt):
        """Что-то типо 'анимации' вектора наклона в сторону вектора движения"""
        self.rotation = self.rotation.lerp(
            self.direction, min(self.turning_speed * dt / 1000, 1))

    def update(self, dt) -> None:
        self.getInput()

        if self.direction:
            self.is_moving = True

            # Наклон спрайта (Изменить вектор наклона, получить угол, повернуть изображение, поставить на прошлое место)
            self.tweenRotation(dt)
            newDegree = -self.getAngle()
            self.image = pygame.transform.rotate(self.originalImage, newDegree)
            self.rect = self.image.get_rect(center=self.rect.center)

            self.direction.normalize_ip()
            newPos = self.rect.center + \
                     (self.direction * self.speed * dt / 1000)
            if self.collideables:
                for rect in self.collideables:
                    if rect.collidepoint(newPos):
                        return False

            self.rect.center = newPos
        else:
            self.is_moving = False


class Turret(Structure):
    distance = 500
    firerate = 4  # Bullets per second

    def __init__(self, name, image, health, *groups) -> None:
        super().__init__(name, 'Turret', image, health, *groups)
        self.idle = 0

    def find_closest_enemy(self, mobs):
        closest_mob = None
        distance_to_him = 99999
        if mobs:
            for mob in mobs:
                mobPos = pygame.math.Vector2(mob.rect.center)
                turretPos = pygame.math.Vector2(self.rect.center)
                distance = (mobPos - turretPos).magnitude()

                if distance < self.distance:
                    closest_mob = mobPos
                    distance_to_him = distance

        return closest_mob, distance_to_him

    @classmethod
    def set_groups(cls, bg, cg):
        cls.bullet_group = bg
        cls.camera_group = cg

    def update(self, dt, mobs):
        mob_pos, distance = self.find_closest_enemy(mobs)
        self.idle += dt / 1000
        if mob_pos:  # If it was found
            shooting_vector = mob_pos - self.rect.center

            if self.idle > 1 / self.firerate:
                Bullet(self.rect.center, shooting_vector, self.bullet_group, self.camera_group)
                self.idle = 0


class Enemy(Sprite):
    sprite_path = path_to_asset('sprites', 'Enemy.png')
    rendered_image = None

    speed = 300
    turning_speed = 4
    max_health = 10
    display_layer = 3

    def __init__(self, position, *groups) -> None:
        super().__init__(*groups)
        if not self.rendered_image:
            self.__class__.rendered_image = pygame.transform.scale(pygame.image.load(self.sprite_path), (64, 64)).convert_alpha()
        self.image = self.rendered_image.copy()
        self.rect = self.image.get_rect(center=position)
        self.health = self.max_health
        self.rotation = pygame.math.Vector2(0, -1)

        self.walk_schedule = list()
        self.movement_direction = None
        self.destination = None
        self.is_moving = False
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            pygame.event.post(MOB_KILLED)
            self.kill()

    def update(self, dt):
        if self.is_moving:
            self.rotation = self.rotation.lerp(self.movement_direction, min(self.turning_speed * dt / 1000, 1))
            angle = -math.degrees(math.atan2(self.rotation.x, -self.rotation.y))
            self.image = pygame.transform.rotate(self.rendered_image, angle)

            newPos = self.rect.center + self.movement_direction * self.speed * dt / 1000
            self.movement_direction = (self.destination - self.rect.center)
            self.movement_direction.scale_to_length(1)

            self.rect.center = newPos
            if (self.destination - self.rect.center).magnitude() < 5:
                self.rect.center = self.destination
                if self.walk_schedule:
                    next_destination = self.walk_schedule.pop(0)
                    self.move_to(next_destination, force=True)
                else:
                    self.is_moving = False

    def move_to(self, coords, force=False):
        if not self.is_moving or force:
            destination = pygame.math.Vector2(coords)
            movement_direction = destination - pygame.math.Vector2(self.rect.center)
            print(movement_direction)
            movement_direction.scale_to_length(1)

            self.is_moving = True
            self.movement_direction = movement_direction
            self.destination = destination

    def update_walk(self, *coords):
        self.walk_schedule.extend(coords[1:])
        self.move_to(coords[0])












class Tile(Sprite):
    def __init__(self, layer, pos, surf, *groups):
        super().__init__(*groups)
        self.image = surf
        self.rect = surf.get_rect(topleft=pos)
        self.layer = layer


class StaticShadow(Sprite):
    """Создаёт статичную тень объекта путём сдвига и обесцвечивания спрайта. Оптимизирован"""
    offset = pygame.math.Vector2(12, 12)
    display_layer = 2

    def __init__(self, sprite, *groups) -> None:
        super().__init__(*groups)
        self.sprite = sprite
        self.image, self.rect = self.get_shadow()

    def get_shadow(self):
        mask = pygame.mask.from_surface(self.sprite.image).outline()
        image = pygame.Surface(self.sprite.rect.size, pygame.SRCALPHA)
        pygame.draw.polygon(image, (0, 0, 0, 128), mask)
        rect = image.get_rect(center=self.sprite.rect.center + self.offset)
        return image, rect


class VectorShadow(Sprite):
    """
        Создаёт векторную тень. precise=True/False для карт, объектов соответственно.
        Во втором случае обязателен tile_size
    """

    def __init__(self, map_sprite: Sprite, sun_vector: pygame.Vector2, height_multiplier: float, *groups) -> Sprite:
        super().__init__(*groups)
        self.image, self.rect = self.calculateShadow(
            map_sprite, sun_vector, height_multiplier)

    @classmethod
    def calculateShadow(cls, sprite, sun_vector, height_multiplier, precise=True, tile_size=None):
        map_mask = pygame.mask.from_surface(sprite.image)
        map_mask.invert()
        map_outline = map_mask.outline()
        if not precise:
            assert tile_size
            # TODO В будущем для теней от построек. Будет НАМНОГО оптимизированней, но не таким точным.
            pass

        shadow_outline = [0] * len(map_outline)
        for i, point in enumerate(map_outline):
            pointVector = pygame.math.Vector2(point)
            shadowPoint = pointVector.lerp(sun_vector, height_multiplier)
            shadowPoint = pointVector + pointVector - shadowPoint
            shadow_outline[i] = shadowPoint.x, shadowPoint.y

        newSurface = pygame.Surface(map_mask.get_size(), pygame.SRCALPHA)
        for i in range(len(map_outline) - 1):
            polygon = map_outline[i], map_outline[i +
                                                  1], shadow_outline[i + 1], shadow_outline[i]
            pygame.draw.polygon(newSurface, (0, 0, 0, 128), polygon)

        return newSurface, newSurface.get_rect()


class EntityShadow(StaticShadow):
    """Класс для динамичных теней. Требует наличия атрибута is_moving в целях оптимизации"""
    offset = pygame.math.Vector2(12, 15)

    def __init__(self, sprite, *groups) -> None:
        super().__init__(sprite, *groups)
        if not hasattr(sprite, 'is_moving'):
            raise TypeError(f'У спрайта {sprite} нет атрибута is_moving')

    def update(self):
        if self.sprite.is_moving:
            self.image, self.rect = self.get_shadow()


del Sprite, Group, dataclass
