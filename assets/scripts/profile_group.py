import pygame

from assets.scripts.path_module import path_to_asset, path_to_userdata
from config import user
from button import Button, ButtonImage, ButtonGroup
from assets.scripts.auth_window import AuthWindow
from assets.scripts.profile_window import ProfileWindow


class ProfileGroup:
    def __init__(self):
        small_font = pygame.font.Font(path_to_asset('fonts', 'CinnamonCoffeCake.ttf'), 20)

        # Создаём спрайты
        profile_sprite = pygame.image.load(
            path_to_userdata(user.get_avatar(), str(user.get_user_id()))).convert_alpha()

        # Создаём кнопки и добавляем их в группу
        self.profile_button = ButtonImage((1210, 10, 60, 60), profile_sprite)
        self.sign_in_button = Button((1210, 80, 60, 35), 'Sign In', small_font, 'White', '#0496FF', '#006BA6')
        self.sign_up_button = Button((1210, 125, 60, 35), 'Sign Up', small_font, 'White', '#0496FF', '#006BA6')
        self.logout_button = Button((1210, 170, 60, 35), 'Logout', small_font, 'White', '#0496FF', '#006BA6')
        self.buttons = ButtonGroup(self.profile_button, self.sign_in_button, self.sign_up_button,
                                   self.logout_button)

    def show(self, screen):
        self.buttons.update(screen)

    def check_click(self, pos):
        clicked_button = self.buttons.check_click(pos)

        if clicked_button is None:
            return

        if clicked_button is self.profile_button:
            print('Нажата кнопка ПРОФИЛЬ')
            ProfileWindow().exec()
            # Перезагружаем аватарку
            profile_sprite = pygame.image.load(
                path_to_userdata(user.get_avatar(), str(user.get_user_id()))).convert_alpha()
            self.profile_button.set_image(profile_sprite)
        elif clicked_button is self.sign_in_button or clicked_button is self.sign_up_button:
            print('Нажата кнопка SIGN ' + ('IN' if clicked_button is self.sign_in_button else 'UP'))
            AuthWindow(clicked_button is self.sign_in_button).exec()
            # Перезагружаем аватарку
            profile_sprite = pygame.image.load(
                path_to_userdata(user.get_avatar(), str(user.get_user_id()))).convert_alpha()
            self.profile_button.set_image(profile_sprite)
        elif clicked_button is self.logout_button:
            print('Нажата кнопка LOGOUT')
            user.log_out()
            # Перезагружаем аватарку
            profile_sprite = pygame.image.load(
                path_to_userdata(user.get_avatar(), str(user.get_user_id()))).convert_alpha()
            self.profile_button.set_image(profile_sprite)

    def check_hover(self, pos):
        self.buttons.check_hover(pos)
