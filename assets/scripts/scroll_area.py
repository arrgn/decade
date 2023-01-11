import pygame as pg
from typing import Union
from config import user
from assets.scripts.fonts import *


class ScrollArea:
    def __init__(self, rect: Union[pg.Rect, tuple], height: int, margin: int, alpha: int,
                 color: tuple[int, int, int]) -> None:
        self.rect = pg.Rect(rect)
        self.height = height
        self.margin = margin
        self.alpha = alpha
        self.color = color
        self.offset = 0
        self.min = self.rect[3]

        # Задний фон
        self.bg = pg.Surface(self.rect[2:])
        self.bg.set_alpha(self.alpha)
        self.bg.fill(self.color)

        self.reload_content()

    def show(self, screen: pg.Surface):
        screen.blit(self.bg, self.rect, (0, self.offset, self.rect[2], self.rect[3]))

    def reload_content(self):
        # Заполняем скроллер данными
        maps = user.get_maps()
        self.resize_bg(len(maps))
        for i in range(len(maps)):
            # Готовим пространство
            rect = pg.Rect((self.margin, self.margin + self.height * i,
                            self.rect[2] - 2 * self.margin, self.height - 2 * self.margin))
            data = pg.Surface(rect[2:])

            # Создаем тексты
            title = font.render(maps[i][0], True, "#E1FAF9")
            description = small_font.render(maps[i][1], True, "#E1FAF9")
            created = small_font.render(maps[i][2], True, "#E1FAF9")

            # Отрисовываем тексты
            data.blit(title, (self.margin, self.margin))
            data.blit(description, (self.margin, self.margin + title.get_height()))
            data.blit(created, (rect[2] - created.get_width(), self.margin))

            self.bg.blit(data, rect)

    def scroll(self, dy):
        self.offset += dy
        if self.offset < 0:
            self.offset = 0
        if self.offset > self.min:
            self.offset = self.min

    def resize_bg(self, k):
        self.bg = pg.Surface((self.rect[2], max(self.height * k, self.min)))
        self.bg.set_alpha(self.alpha)
        self.bg.fill(self.color)
