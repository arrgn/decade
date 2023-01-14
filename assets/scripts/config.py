from assets.scripts.db_module import DAO
from assets.scripts.user_model import User
from assets.scripts.music_player import MusicPlayer
import json
from assets.scripts.path_module import path_to_asset

path_to_db = "db.db"
# default_user: list[str(username), str(password)]
default_user = ["guest", ""]

release = True

dao = DAO(path_to_db)
user = User(database=dao)
if not dao.get_user_by_name(default_user[0]):
    user.add_user(*default_user)

music_player = MusicPlayer()

path_to_maps_config = path_to_asset("maps", "maps.json")

with open(path_to_maps_config) as file:
    default_levels = json.load(file)
all_levels = list(map(lambda x: x[0], dao.get_maps()))
for k, v in default_levels.items():
    if k not in all_levels:
        user.add_map(k, v["DESCRIPTION"], v["ACCESS"])
