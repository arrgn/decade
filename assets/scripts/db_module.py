from sqlite3 import connect
from assets.scripts.path_module import path_to_file


class DAO:
    class UserExistsError(Exception):
        pass

    class UserDoesntExistError(Exception):
        pass

    class MapNotFoundError(Exception):
        pass

    def __init__(self, path_to_db="db.db"):
        self.con = connect(path_to_file(path_to_db))
        self.cur = self.con.cursor()
        build = """
CREATE TABLE IF NOT EXISTS users
(
    id       INTEGER PRIMARY KEY UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE        NOT NULL,
    password VARCHAR(255)               NOT NULL,
    avatar   TEXT
);
        """
        self.cur.execute(build)
        build = """
CREATE TABLE IF NOT EXISTS maps
(
    id          INTEGER PRIMARY KEY UNIQUE NOT NULL,
    title       VARCHAR(255)               NOT NULL,
    description VARCHAR(255)               NOT NULL,
    created     VARCHAR(255)               NOT NULL,
    file        VARCHAR(255)               NOT NULL
);
        """
        self.cur.execute(build)
        build = """
CREATE TABLE IF NOT EXISTS usermap
(
    user_id INTEGER NOT NULL,
    map_id  INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (map_id) REFERENCES maps (id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, map_id)
);
        """
        self.cur.execute(build)

    def get_users(self):
        sql = """SELECT username FROM users WHERE username!='guest'"""
        res = self.cur.execute(sql)
        return list(res)

    def get_user_by_name(self, name):
        sql = """SELECT id, username, avatar FROM users WHERE username=?"""
        res = self.cur.execute(sql, [name])
        return list(res)

    def get_user_by_id(self, user_id):
        sql = """SELECT id, username, avatar FROM users WHERE id=?"""
        res = self.cur.execute(sql, [user_id])
        return list(res)

    def get_checked_user(self, name, password):
        if not self.get_user_by_name(name):
            raise self.UserDoesntExistError(f"user with name {name} doesnt exist")
        sql = """SELECT id, username, avatar FROM users WHERE username=? AND password=?"""
        res = self.cur.execute(sql, [name, password])
        return list(res)

    def add_user(self, name, passwd):
        user = self.get_user_by_name(name)
        if user:
            raise self.UserExistsError(f"user with name {name} already exists")
        sql = """INSERT INTO users(username, password) VALUES(?, ?)"""
        res = self.cur.execute(sql, [name, passwd])
        self.change_avatar(name)
        self.con.commit()
        return list(res)

    def change_username(self, old_name, new_name):
        user = self.get_user_by_name(old_name)
        if not user:
            raise self.UserDoesntExistError(f"user with name {old_name} doesnt exist")
        candidate = self.get_user_by_name(new_name)
        if candidate:
            raise self.UserExistsError(f"user with name {new_name} already exists")
        sql = """UPDATE users SET username=? WHERE id=?"""
        res = self.cur.execute(sql, [new_name, user[0][0]])
        self.con.commit()
        return res

    def change_avatar(self, name, avatar="default.png"):
        user = self.get_user_by_name(name)
        if not user:
            raise self.UserDoesntExistError(f"user with name {name} doesnt exist")
        sql = """UPDATE users SET avatar=? WHERE id=?"""
        res = self.cur.execute(sql, [avatar, user[0][0]])
        self.con.commit()
        return res

    def delete_user_by_name(self, name):
        if not self.get_user_by_name(name):
            raise self.UserDoesntExistError(f"user with name {name} doesnt exist")
        sql = """DELETE FROM users WHERE username=?"""
        res = self.cur.execute(sql, [name])
        self.con.commit()
        return list(res)

    def add_map(self, name, title, description, created, file):
        user = self.get_user_by_name(name)
        if not user:
            raise self.UserDoesntExistError(f"user with name {name} doesn't exist")
        sql = """INSERT INTO maps(title, description, created, file) VALUES (?, ?, ?, ?)"""
        res = list(self.cur.execute(sql, [title, description, created, file]))
        sql = """INSERT INTO usermap VALUES (?, ?)"""
        res += list(self.cur.execute(sql, [user[0][0], self.cur.lastrowid]))
        self.con.commit()
        return res

    def get_maps_by_user(self, name):
        user = self.get_user_by_name(name)
        if not user:
            raise self.UserDoesntExistError(f"user with name {name} doesn't exist")
        sql = """SELECT title, description, created, file FROM maps JOIN usermap ON (user_id=? OR user_id=0)"""
        res = self.cur.execute(sql, [user[0][0]])
        return list(res)

    def get_map(self, username, map_name):
        user = self.get_user_by_name(username)
        if not user:
            raise self.UserDoesntExistError(f"user with name {username} doesn't exist")
        sql = """SELECT * FROM maps JOIN usermap ON (map_id=id AND (user_id=? OR user_id=0)) WHERE title=?"""
        res = self.cur.execute(sql, [user[0][0], map_name])
        return list(res)

    def access_map(self, name_from, name_to, map_name):
        # get_map will check if user_from exists
        user_to = self.get_user_by_name(name_to)
        if not user_to:
            raise self.UserDoesntExistError(f"user with name {name_to} doesn't exist")
        map_ = self.get_map(name_from, map_name)
        if not map_:
            raise self.MapNotFoundError(f"map with title {map_name} doesn't exist")
        sql = """INSERT INTO usermap VALUES (?, ?)"""
        res = self.cur.execute(sql, [user_to[0][0], map_[0][0]])
        self.con.commit()
        return list(res)
