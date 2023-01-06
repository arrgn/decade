import math

import pygame
import time
from os.path import join
from pygame.sprite import Sprite

TILE_WIDTH = TILE_HEIGHT = 32
LEVEL_WIDTH, LEVEL_HEIGHT = 95 * TILE_WIDTH, 95 * TILE_HEIGHT

class Player(Sprite):
    accelerated_speed = 900
    regular_speed = 500
    turning_speed = 5
    max_health = 15

    def __init__(self, pos, collideables=None, *groups):
        super().__init__(*groups)
        image = pygame.image.load(join('assets', 'sprites', 'Character.png')).convert_alpha()
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

    def getAngle(self):
        """Получить угол наклона в градусах из вектора наклона"""

        # Перед координатой Y стоит унарный минус потому что координаты
        # в pygame работают по уё.. другому.
        return math.degrees(math.atan2(self.rotation.x, -self.rotation.y))

    def tweenRotation(self, dt):
        """Что-то типо 'анимации' вектора наклона в сторону вектора движения"""
        self.rotation = self.rotation.lerp(self.direction, min(self.turning_speed * dt / 1000, 1))

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
            newPos = self.rect.center + (self.direction * self.speed * dt / 1000)
            if self.collideables:
                for rect in self.collideables:
                    if rect.collidepoint(newPos):
                        return False

            self.rect.center = newPos
        else:
            self.is_moving = False


class Tile(Sprite):
    def __init__(self, layer, pos, surf, *groups):
        super().__init__(*groups)
        self.image = surf
        self.rect = surf.get_rect(topleft=pos)
        self.layer = layer


class StaticShadow(Sprite):
    """Создаёт статичную тень объекта путём сдвига и обесцвечивания спрайта. Оптимизирован"""
    offset = pygame.math.Vector2(12, 12)

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
        self.image, self.rect = self.calculateShadow(map_sprite, sun_vector, height_multiplier)

    @classmethod
    def calculateShadow(cls, sprite, sun_vector, height_multiplier, precise=True, tile_size=None):
        map_mask = pygame.mask.from_surface(sprite.image)
        map_mask.invert()
        map_outline = map_mask.outline()
        if not precise:
            assert tile_size
            pass  # TODO В будущем для теней от построек. Будет НАМНОГО оптимизированней, но не таким точным.

        shadow_outline = [0] * len(map_outline)
        for i, point in enumerate(map_outline):
            pointVector = pygame.math.Vector2(point)
            shadowPoint = pointVector.lerp(sun_vector, height_multiplier)
            shadowPoint = pointVector + pointVector - shadowPoint
            shadow_outline[i] = shadowPoint.x, shadowPoint.y

        newSurface = pygame.Surface(map_mask.get_size(), pygame.SRCALPHA)
        for i in range(len(map_outline) - 1):
            polygon = map_outline[i], map_outline[i + 1], shadow_outline[i + 1], shadow_outline[i]
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

del Sprite