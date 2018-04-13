import os
import yaml


def read_yaml(path: str) -> dict:
    with open(path, 'r', encoding='utf8') as fd:
        return yaml.load(fd, Loader=yaml.Loader)


def get_config_from_env() -> dict:
    config_path = os.getenv('CONFIG_PATH', '')
    if not config_path:
        # TODO: raize config exception
        return {}
    config = read_yaml(config_path)
    return config or {}

