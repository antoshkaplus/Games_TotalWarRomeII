import json


def load_config():
    with open("./config.json", 'r') as f:
        config = json.load(f)
    return config


config = load_config()


def get_games_db_path():
    return config["GamesDbPath"]


def get_fixed_db_path():
    return config["FixedDbPath"]