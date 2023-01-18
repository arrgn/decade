import pygame

from assets.scripts.path_module import path_to_userdata
from assets.scripts.configuration.config import user
from assets.scripts.ui.button import Button, ButtonImage, ButtonGroup
from assets.scripts.QT.auth_window import AuthWindow
from assets.scripts.QT.profile_window import ProfileWindow
from assets.scripts.instances.fonts import small_font


class ProfileGroup:
    def __init__(self, top_right, width, height, margin):
        self.top_right = top_right
        self.height = height
        self.width = width
        self.margin = margin

        # Создаём спрайты
        profile_sprite = pygame.image.load(
            path_to_userdata(user.get_avatar(), str(user.get_user_id()))).convert_alpha()

        start_x = top_right[0] - width - margin
        # Создаём кнопки и добавляем их в группу
        self.profile_button = ButtonImage((start_x, margin, width, width), profile_sprite)
        self.sign_in_button = Button((start_x, self.profile_button.rect.bottomleft[1] + margin, width, height),
                                     'Sign In', small_font, 'White', '#0496FF', '#006BA6')
        self.sign_up_button = Button((start_x, self.sign_in_button.rect.bottomleft[1] + margin, width, height),
                                     'Sign Up', small_font, 'White', '#0496FF', '#006BA6')
        self.logout_button = Button((start_x, self.sign_up_button.rect.bottomleft[1] + margin, width, height), 'Logout',
                                    small_font, 'White', '#0496FF', '#006BA6')
        self.buttons = ButtonGroup(self.profile_button, self.sign_in_button, self.sign_up_button,
                                   self.logout_button)

    def show(self, screen):
        self.buttons.update(screen)

    def check_click(self, pos):
        clicked_button = self.buttons.check_click(pos)

        if clicked_button is None:
            return True

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
        return False

    def check_hover(self, pos):
        self.buttons.check_hover(pos)
