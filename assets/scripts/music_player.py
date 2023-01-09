import pygame as pg

from assets.scripts.path_module import path_to_asset


class MusicPlayer:
    def __init__(self, default: str = None, repeat: int = -1, volume: float = 1, sounds: dict[str: str] = None) -> None:
        """
            Класс для управления музыкой и звуками
            @param default фоновая музыка по умолчанию
            @param repeat количество раз проигрывания фоновой музыки (по умолчанию - зацикливание)
            @param volume громкость (0 - 1)
            @param sounds звуки для проигрывания во время игры
        """
        pg.mixer.init()
        self.sounds = {}
        if default:
            pg.mixer.music.load(path_to_asset("music", default))
            pg.mixer.music.set_volume(volume)
            pg.mixer.music.play(repeat)
        if sounds:
            for k, v in sounds.items():
                self.sounds[k] = pg.mixer.Sound(path_to_asset("music", v))

    def add_sound(self, name: str, file: str) -> None:
        """
            Добавляет звук в коллекцию
            @param name имя звука
            @param file имя файла
        """
        self.sounds[name] = pg.mixer.Sound(path_to_asset("music", file))

    def play_sound(self, name: str, loops: int = 0, max_time: int = 0, fade_ms: int = 0) -> None:
        """
            Проигрывает звук из коллекции
            @param name название файла
            @param loops количество циклов проигрывания (по умолчанию 1 раз, отсчет с 0)
            @param max_time максимальное время проигрывания в мс
            @param fade_ms время, за которое музыка будет наращивать громкость с 0 до 1 с начала проигрывания
        """
        self.sounds[name].play(loops=loops, maxtime=max_time, fade_ms=fade_ms)

    def set_volume(self, name: str, volume: float):
        """
            Устанавливает громкость для звука
            @param name имя звука
            @param volume громкость (0 - 1)
        """
        self.sounds[name].set_volume(volume)

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
