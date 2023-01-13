import typing
import pygame as pg

from assets.scripts.path_module import path_to_asset
from typing import Union

# Инициализация миксера
pg.mixer.init()


class MusicPlayer:
    """
        Класс для управления музыкой и звуками
    """

    class Sound:
        """
            Класс для легкого управления звуками
        """

        def __init__(self, file: str, loops: int = 0, max_time: int = 0, fade_ms: int = 0, volume: int = 1,
                     mult: float = 1) -> None:
            """
                @param file название файла
                @param loops количество циклов проигрывания (по умолчанию 1 раз, отсчет с 0)
                @param max_time максимальное время проигрывания в мс
                @param fade_ms время, за которое музыка будет наращивать громкость с 0 до 1 с начала проигрывания
                @param volume громкость (0 - 1)
                @param mult коэффициент громкости
            """
            self.sound = pg.mixer.Sound(path_to_asset("music", file))
            self.loops = loops
            self.max_time = max_time
            self.fade_ms = fade_ms
            self.volume = volume
            self.mult = mult

            self.sound.set_volume(self.volume * self.mult)

        def __call__(self) -> None:
            """
                Проигрывает звук
            """
            self.sound.play(self.loops, self.max_time, self.fade_ms)

        def change_config(self, loops: int = None, max_time: int = None, fade_ms: int = None,
                          volume: float = None, mult: float = None) -> None:
            """
                Изменяет текущие настройки звука
                @param loops количество циклов проигрывания (по умолчанию 1 раз, отсчет с 0)
                @param max_time максимальное время проигрывания в мс
                @param fade_ms время, за которое музыка будет наращивать громкость с 0 до 1 с начала проигрывания
                @param volume громкость (0 - 1)
                @param mult коэффициент громкости
            """
            if loops:
                self.loops = loops
            if max_time:
                self.max_time = max_time
            if fade_ms:
                self.fade_ms = fade_ms
            if volume:
                self.volume = volume
                self.sound.set_volume(self.volume * self.mult)
            if mult:
                self.mult = mult
                self.sound.set_volume(self.volume * self.mult)

        def set_sound(self, file: str) -> None:
            """
                Изменяет звук (громкость остается прежней)
                @param file название файла
            """
            self.sound = pg.mixer.Sound(path_to_asset("music", file))
            self.sound.set_volume(self.volume * self.mult)

    def __init__(self, default: str = None, repeat: int = -1, volume: float = 1, mult: float = 1,
                 sounds: typing.Dict[str, Union[typing.Dict[str, str], Sound]] = None) -> None:
        """
            @param default фоновая музыка по умолчанию
            @param repeat количество раз проигрывания фоновой музыки (по умолчанию - зацикливание)
            @param volume громкость (0 - 1)
            @param mult коэффициент громкости
            @param sounds звуки для проигрывания во время игры
        """
        self.sounds: typing.Dict[str, MusicPlayer.Sound] = {}
        self.bg_volume = volume
        if default:
            pg.mixer.music.load(path_to_asset("music", default))
            pg.mixer.music.set_volume(self.bg_volume * mult)
            pg.mixer.music.play(repeat)
        if sounds:
            for k, v in sounds.items():
                self[k] = v

    def change_sound_config(self, name: str, loops: int = None, max_time: int = None, fade_ms: int = None,
                            volume: float = None, mult: float = None) -> None:
        """
            Изменяет настройки звука
            @param name имя звука
            @param loops количество циклов проигрывания (по умолчанию 1 раз, отсчет с 0)
            @param max_time максимальное время проигрывания в мс
            @param fade_ms время, за которое музыка будет наращивать громкость с 0 до 1 с начала проигрывания
            @param volume громкость (0 - 1)
            @param mult коэффициент громкости
        """
        pg.mixer.music.set_volume(self.bg_volume * mult)
        if name in self.sounds:
            self.sounds[name].change_config(loops, max_time, fade_ms, volume, mult)

    def set_global_volume(self, mult: float) -> None:
        """
            Изменяет громкость у всех звуков
            @param mult коэффициент громкости
        """
        pg.mixer.music.set_volume(self.bg_volume * mult)
        for k, sound in self.sounds.items():
            sound.change_config(mult=mult)

    def __setitem__(self, key: str, value: Union[typing.Dict[str, str], Sound]) -> None:
        """
            Добавляет звук в коллекцию
            @param key имя звука
            @param value объект класса MusicPlayer.Sound или словарь (ключи - аргументы MusicPlayer.Sound)
        """
        if type(value) == MusicPlayer.Sound:
            self.sounds[key] = value
            return
        self.sounds[key] = MusicPlayer.Sound(**value)

    def __getitem__(self, item: str) -> Union[None, Sound]:
        """
            Возвращает звук из коллекции
            @param item имя звука
        """
        if item in self.sounds:
            return self.sounds[item]
        return None

    def __delitem__(self, key: str) -> None:
        """
            Удаляет звук из коллекции
            @param key имя звука
        """
        if key in self.sounds:
            del self.sounds[key]

    def __call__(self, name: str) -> None:
        """
            Проигрывает звук из коллекции
            @param name название файла
        """
        if name in self.sounds:
            self.sounds[name]()

    @staticmethod
    def add_bg_music(background: str) -> None:
        """
            Добавляет фоновую музыку в очередь на проигрывание
            @param background имя файла с музыкой
        """
        pg.mixer.music.queue(path_to_asset("music", background))

    @staticmethod
    def play_bg_music(background: str, repeat: int = -1, volume: float = 1) -> None:
        """
            Устанавливает фоновую музыку
            @param background имя файла
            @param repeat количество повторов (по умолчанию - бесконечно)
            @param volume громкость (0 - 1)
        """
        pg.mixer.music.load(path_to_asset("music", background))
        pg.mixer.music.set_volume(volume)
        pg.mixer.music.play(repeat)
