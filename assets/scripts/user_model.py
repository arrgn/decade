from assets.scripts.db_module import DAO
from assets.scripts.path_module import path_to_userdata, copy_file, create_user_dir
from assets.scripts.loggers import logger
from datetime import datetime


class User:
    def __init__(self, database=None):
        self.name = "guest"
        self.id = 1
        self.dao = None
        if database is not None:
            self.dao = database

    def log_out(self):
        try:
            res = self.dao.get_user_by_id(1)
            self.name = res[0][1]
            self.id = 1
            return res
        except DAO.UserDoesntExistError:
            logger.exception("Tracked exception occurred!")
        return False

    def add_user(self, name, password):
        try:
            self.dao.add_user(name, password)
            self.name = name
            self.id = str(self.dao.get_user_by_name(self.name)[0][0])
            create_user_dir(self.id)
            copy_file(path_to_userdata("default.png", "default"), self.id)
            return True
        except DAO.UserExistsError:
            logger.exception("Tracked exception occurred!")
        return False

    def set_user(self, name, password):
        try:
            res = self.dao.get_checked_user(name, password)
            self.name = name
            self.id = str(self.dao.get_user_by_name(self.name)[0][0])
            return res
        except DAO.UserDoesntExistError:
            logger.exception("Tracked exception occurred!")
        return False

    def get_user(self):
        return self.name

    def get_user_id(self):
        return self.id

    def get_users(self):
        return self.dao.get_users()

    def get_avatar(self):
        try:
            res = self.dao.get_user_by_name(self.name)
            if not res:
                raise DAO.UserDoesntExistError(f"user with name {self.name} doesnt exist")
            return res[0][2]
        except DAO.UserDoesntExistError:
            logger.exception("Tracked exception occurred!")
        return False

    def change_username(self, new_name):
        try:
            self.dao.change_username(self.name, new_name)
            self.name = new_name
            return True
        except DAO.UserDoesntExistError:
            logger.exception("Tracked exception occurred!")
        except DAO.UserExistsError:
            logger.exception("Tracked exception occurred!")
        return False

    def change_avatar(self, avatar="default.png"):
        try:
            self.dao.change_avatar(self.name, avatar)
            return True
        except DAO.UserDoesntExistError:
            logger.exception("Tracked exception occurred!")
        return False

    def delete_user(self):
        try:
            res = self.dao.delete_user_by_name(self.name)
            return res
        except DAO.UserDoesntExistError:
            logger.exception("Tracked exception occurred!")
        return False

    def add_map(self, title, description, map_type):
        try:
            self.dao.add_map(self.get_user(), title, description, datetime.now(), map_type)
            return True
        except DAO.UserDoesntExistError:
            logger.exception("Tracked exception occurred!")
        return False

    def get_maps(self):
        try:
            res = self.dao.get_maps_by_user(self.get_user())
            out = {}
            for el in res:
                out[el[0]] = {
                    "DESCRIPTION": el[1],
                    "DATE": el[2],
                    "SCORE": el[3],
                }
            print("!" * 100)
            print(*res, sep="\n")
            return out
        except DAO.UserDoesntExistError:
            logger.exception("Tracked exception occurred!")
        return []

    def get_map(self, name):
        try:
            res = self.dao.get_map(self.get_user(), name)
            return res
        except (DAO.UserDoesntExistError, DAO.MapNotFoundError):
            logger.exception("Tracked exception occurred!")
        return False

    def access_map(self, user_to, map_name):
        try:
            self.dao.access_map(self.get_user(), user_to, map_name)
            return True
        except (DAO.UserDoesntExistError, DAO.MapNotFoundError):
            logger.exception("Tracked exception occurred!")
        return False

    def save_score(self, map_name, score):
        try:
            self.dao.save_score(self.get_user(), map_name, score)
            return True
        except (DAO.UserDoesntExistError, DAO.MapNotFoundError):
            logger.exception("Tracked exception occurred!")
        return False
