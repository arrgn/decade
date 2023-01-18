import sys
import json
import pygame
from assets.scripts.path_module import path_to_file
from assets.scripts.configuration.config import config


def save_and_exit():
    with open(path_to_file("config.json"), mode="w") as f:
        print(config.__dict__)
        json.dump(config.__dict__, f, indent=2)
    pygame.quit()
    sys.exit()
