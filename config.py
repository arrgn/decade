from assets.scripts.db_module import DAO
from assets.scripts.user_model import User
from assets.scripts.music_player import MusicPlayer

path_to_db = "db.db"
# default_user: list[str(username), str(password)]
default_user = ["guest", ""]
# default_maps: list[list[str(title), str(description), str(file)]]
default_maps = [["Default", "The first created map", "Map.tmx"], ["MFW", "My first world", "nya?"],
                ["HARDCORE", "The hardest world in the history!", "hard"]]

release = True

dao = DAO(path_to_db)
user = User(database=dao)
if not dao.get_user_by_name(default_user[0]):
    user.add_user(*default_user)

for map_ in default_maps:
    if not user.get_map(map_[0]):
        user.add_map(*map_)

music_player = MusicPlayer()
