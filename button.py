import pygame


class Button(pygame.sprite.Sprite):
    def __init__(self, rect: pygame.Rect | tuple, text: str, font: pygame.font.Font, text_color: str | tuple, btn_color: str | tuple, hover_color: str | tuple) -> None:
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
            B положительном случае перерисовывает кнопку в другой цвет.
            Возвращает True/False в зависимости от результата.
        """
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color
            return True
        elif self.current_color == self.hover_color:
            self.current_color = self.btn_color
        return False


class ButtonGroup(pygame.sprite.Group):
    def __init__(self, *sprites) -> None:
        super().__init__(*sprites)

    def check_hover(self, pos: tuple[int, int]) -> None:
        """Вызывает срабатывание check_hover() метода во всех кнопках в группе. Ничего не возвращает"""
        for button in self.sprites():
            if button.check_hover(pos):
                break

    def check_click(self, pos: tuple[int, int]) -> Button | None:
        """
            Проверяет, была ли нажата какая либо кнопка в группе.
            Вызывать этот метод только в pygame.event.get()
            Проверка на само нажатие производится только там.
            Возвращает кнопку или None.
        """
        for button in self.sprites():
            if button.rect.collidepoint(pos):
                return button
