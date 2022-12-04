import pygame
import sys


class Game:
    FPS = 60

    def __init__(self, width, height) -> None:
        pygame.init()
        pygame.display.set_caption('Untitled')
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        pygame.display.update()
        

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.clock.tick(self.FPS)
            pygame.display.update()


if __name__ == "__main__":
    mainWindow = Game(1280, 720)
    mainWindow.run()