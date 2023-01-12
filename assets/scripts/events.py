import pygame

# Аттрибуты должны быть одинаковыми, чтобы сравнение вернуло True.
# Так что можно указывать нужные аттрибуты, вместо увеличения `type`
SAVE_AND_RETURN = pygame.event.Event(pygame.USEREVENT, action="save and return")
