import pygame
from assets.scripts.path_module import path_to_asset

pygame.font.init()

small_font = pygame.font.Font(path_to_asset('fonts', 'CinnamonCoffeCake.ttf'), 20)
font = pygame.font.Font(path_to_asset('fonts', 'CinnamonCoffeCake.ttf'), 35)
big_font = pygame.font.Font(path_to_asset('fonts', 'CinnamonCoffeCake.ttf'), 100)
