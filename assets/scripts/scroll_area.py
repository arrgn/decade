import pygame as pg
from typing import Union, Callable, Any
from assets.scripts.fonts import *
from assets.scripts.button import SurfaceButton, ButtonGroup


class ScrollArea:
    def __init__(self, rect: Union[pg.Rect, tuple], height: int, margin: int, alpha: int,
                 color: tuple[int, int, int], get_data: Callable[[], dict],
                 send_data: Callable[[Any], Any]) -> None:
        self.rect = pg.Rect(rect)
        self.height = height
        self.margin = margin
        self.alpha = alpha
        self.color = color
        self.offset = 0
        self.min = self.rect[3]
        self.get_data = get_data
        self.send_data = send_data
        self.buttons = []
        self.button_group: ButtonGroup = ButtonGroup()

        # Задний фон
        self.bg = pg.Surface(self.rect[2:])
        self.bg.set_alpha(self.alpha)
        self.bg.fill(self.color)

        self.reload_content()

    def show(self, screen: pg.Surface):
        self.button_group.update(self.bg)
        screen.blit(self.bg, self.rect, (0, self.offset, self.rect[2], self.rect[3]))

    def reload_content(self):
        # Заполняем скроллер данными
        maps = self.get_data()
        self.buttons.clear()
        self.resize_bg(len(maps))
        i = 0
        for k, v in maps.items():
            # Готовим пространство
            rect = pg.Rect((self.margin, self.margin + self.height * i,
                            self.rect[2] - 2 * self.margin, self.height - 2 * self.margin))
            data = pg.Surface(rect[2:])

            # Создаем тексты
            title = font.render(k + (f" ({v['SCORE']})" if v["SCORE"] else ""), True, "#E1FAF9")
            description = small_font.render(v["DESCRIPTION"], True, "#E1FAF9")
            created = small_font.render(v["DATE"], True, "#E1FAF9")

            # Отрисовываем тексты
            data.blit(title, (self.margin, self.margin))
            data.blit(description, (self.margin, self.margin + title.get_height()))
            data.blit(created, (rect[2] - created.get_width(), self.margin))

            self.buttons.append(SurfaceButton(rect, data, k))
            i += 1

        self.button_group.change_buttons(*self.buttons)

    def scroll(self, dy):
        dy *= 30  # either scrolling is too slow
        self.offset += dy
        if self.offset < 0:
            self.offset = 0
        if self.offset > self.min - self.rect[3]:
            self.offset = self.min - self.rect[3]

    def resize_bg(self, k):
        self.min = max(self.rect[3], self.height * k)
        self.bg = pg.Surface((self.rect[2], self.min))
        self.bg.set_alpha(self.alpha)
        self.bg.fill(self.color)

    def check_click(self, pos):
        clicked_button = self.button_group.check_click((pos[0], pos[1] + self.offset - self.rect[1]))

        if clicked_button is None:
            return True

        for button in self.buttons:
            if clicked_button is button:
                self.send_data(button.data)
                break
        else:
            return True
        return False
