import shutil

from os import path, makedirs
from os.path import basename, isdir
from assets.scripts.loggers import logger


def path_to_file(*elements) -> str:
    """
    :param elements: parts of local path to file (or directory)
    :return: string - full path to file (or directory)
    """
    return path.join(*elements)


def path_to_asset(*elements) -> str:
    """
    :param elements: parts of local path to file (or directory)
    :return: string - full path to file (or directory)
    """
    return path.join("assets", *elements)


def path_to_userdata(filename: str, user_id: str) -> str:
    """
    :return: path to file from user's folder
    """
    return path_to_file("userdata", user_id, filename)


def copy_user_file(src, username):
    try:
        shutil.copy(src, path_to_userdata(basename(src), username))
    except shutil.SameFileError:
        logger.exception("Tracked exception occurred!")


def copy_file(src, dist):
    try:
        shutil.copy(src, path_to_file(*dist))
    except shutil.SameFileError:
        logger.exception("Tracked exception occurred!")


def create_user_dir(username):
    """
    Create dir for current user in userdata
    """
    try:
        makedirs(path_to_userdata("", username))
    except FileExistsError:
        logger.exception("Tracked exception occurred!")


def create_dir(*dirname):
    try:
        if not isdir(path_to_file(*dirname)):
            makedirs(path_to_file(*dirname))
    except FileExistsError:
        logger.exception("Tracked exception occurred!")
