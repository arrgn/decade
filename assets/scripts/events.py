import pygame

# Аттрибуты должны быть одинаковыми, чтобы сравнение вернуло True.
# Так что можно указывать нужные аттрибуты, вместо увеличения `type`
SAVE_AND_RETURN = pygame.event.Event(pygame.USEREVENT, action="save and return")
WAVE_CLEARED = pygame.event.Event(pygame.USEREVENT, action="wave cleared")
WAVE_STARTS = pygame.event.Event(pygame.USEREVENT, action="wave starts")
GAME_ENDED = pygame.event.Event(pygame.USEREVENT, action='game ended')
