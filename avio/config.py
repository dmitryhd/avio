import yaml


def read_yaml(path: str) -> dict:
    with open(path, 'r', encoding='utf8') as fd:
        return yaml.load(fd, Loader=yaml.Loader)
