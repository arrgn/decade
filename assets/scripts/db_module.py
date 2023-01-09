from sqlite3 import connect
from assets.scripts.path_module import path_to_file


class DAO:
    class UserExistsError(Exception):
        pass

    class UserDoesntExistError(Exception):
        pass

    class WorkspaceNotFoundError(Exception):
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

    def get_users(self):
        sql = """SELECT username FROM users WHERE username!=\"guest\""""
        res = self.cur.execute(sql)
        return list(res)

    def get_user_by_name(self, name):
        sql = """SELECT id, username, avatar FROM users WHERE username=?"""
        res = self.cur.execute(sql, [name])
        return list(res)

    def get_user_by_id(self, id):
        sql = """SELECT id, username, avatar FROM users WHERE id=?"""
        res = self.cur.execute(sql, [id])
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
