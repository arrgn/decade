import pygame
from typing import Union


class Button(pygame.sprite.Sprite):
    def __init__(self, rect: Union[pygame.Rect, tuple], text: str, font: pygame.font.Font,
                 text_color: Union[str, tuple], btn_color: Union[str, tuple], hover_color: Union[str, tuple]) -> None:
        super().__init__()
        self.rect = pygame.Rect(rect)
        self.font = font
        self.text_color = text_color
        self.btn_color = btn_color
        self.current_color = self.btn_color
        self.hover_color = hover_color
        self.text = self.font.render(text, True, self.text_color)

    def update(self, screen: pygame.Surface) -> None:
        """
            Отрисовывает кнопку на экране. Ничего не возвращает
            He забыть обновить сам экран через pygame.display.update()
        """
        pygame.draw.rect(screen, self.current_color, self.rect)
        screen.blit(self.text, self.text.get_rect(center=self.rect.center))

    def check_hover(self, pos: tuple[int, int]) -> bool:
        """
            Проверяет наличие курсора на кнопке.
            В положительном случае перерисовывает кнопку в другой цвет.
            Возвращает True/False в зависимости от результата.
        """
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color
            return True
        elif self.current_color == self.hover_color:
            self.current_color = self.btn_color
        return False


class ButtonImage(pygame.sprite.Sprite):
    def __init__(self, rect: Union[pygame.Rect, tuple], image: pygame.Surface,
                 hover_color: tuple[float, float, float, float] = (1, 1, 1, 0.8)) -> None:
        super().__init__()
        self.rect = pygame.Rect(rect)
        self.normal_image = pygame.transform.smoothscale(image, self.rect[2:])
        self.hover_color = hover_color
        self.hover_image = self.filter(self.normal_image, self.hover_color)
        self.image = self.normal_image

    def update(self, screen: pygame.Surface) -> None:
        """
            Отрисовывает кнопку на экране. Ничего не возвращает
            He забыть обновить сам экран через pygame.display.update()
        """
        screen.blit(self.image, self.rect)

    def check_hover(self, pos: tuple[int, int]) -> bool:
        """
            Проверяет наличие курсора на кнопке.
            В положительном случае перерисовывает кнопку в другой цвет.
            Возвращает True/False в зависимости от результата.
        """
        if self.rect.collidepoint(pos):
            self.image = self.hover_image
            return True
        else:
            self.image = self.normal_image
        return False

    def set_image(self, image: pygame.Surface):
        """
            Устанавливает новое изображение на кнопку
        """
        self.normal_image = pygame.transform.smoothscale(image, self.rect[2:])
        self.hover_image = self.filter(self.normal_image, self.hover_color)
        self.image = self.normal_image

    @staticmethod
    def filter(image: pygame.surface, color: tuple[float, float, float, float]) -> pygame.surface:
        """
            Применяет цветовой фильтр к изображению
            @param image: изображение (не будет изменено)
            @param color: коэффициенты для домножения для каждого параметра rgba
            @return измененное изображение
        """
        image = pygame.Surface.copy(image).convert_alpha()
        w, h = image.get_size()
        kr, kg, kb, ka = color
        for x in range(w):
            for y in range(h):
                r, g, b, a = image.get_at((x, y))
                r = int(r * kr)
                g = int(g * kg)
                b = int(b * kb)
                a = int(a * ka)
                image.set_at((x, y), pygame.Color(r, g, b, a))
        return image


class SurfaceButton(pygame.sprite.Sprite):
    def __init__(self, rect: Union[tuple, pygame.Rect], image: pygame.Surface, data: str) -> None:
        super().__init__()
        self.rect = pygame.Rect(rect)
        self.image = image
        self.data = data

    def update(self, screen: pygame.Surface) -> None:
        """
            Отрисовывает кнопку на экране. Ничего не возвращает
            He забыть обновить сам экран через pygame.display.update()
        """
        screen.blit(self.image, self.rect)


class ButtonGroup(pygame.sprite.Group):
    def __init__(self, *sprites) -> None:
        super().__init__(*sprites)

    def check_hover(self, pos: tuple[int, int]) -> None:
        """Вызывает срабатывание check_hover() метода во всех кнопках в группе. Ничего не возвращает"""
        for button in self.sprites():
            if button.check_hover(pos):
                break

    def check_click(self, pos: tuple[int, int]) -> Union[Button, None]:
        """
            Проверяет, была ли нажата какая-либо кнопка в группе.
            Вызывать этот метод только в pygame.event.get()
            Проверка на само нажатие производится только там.
            Возвращает кнопку или None.
        """
        for button in self.sprites():
            if button.rect.collidepoint(pos):
                return button

    def change_buttons(self, *sprites):
        super().__init__(*sprites)
