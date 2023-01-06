from assets.scripts.db_module import DAO
from assets.scripts.user_model import User

path_to_db = "db.db"
# default_user: list[str(username), str(password)]
default_user = ["guest", ""]

release = True

dao = DAO(path_to_db)
user = User(database=dao)
if not dao.get_user_by_name(default_user[0]):
    user.add_user(*default_user)
