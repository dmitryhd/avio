import os
import yaml


def read_config(path: str) -> dict:
    with open(path, 'r', encoding='utf8') as fd:
        return yaml.safe_load(fd)


def get_config_from_env() -> dict:
    config_path = os.getenv('CONFIG_PATH', '')
    if not config_path:
        # TODO: raize config exception
        return {}
    config = read_config(config_path)
    return config or {}
