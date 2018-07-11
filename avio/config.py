import os
import yaml
from copy import deepcopy


class ConfigParser:

    def __init__(self, initial_config: dict = None):
        if not initial_config:
            initial_config = {}
        self._default_config = deepcopy(initial_config)
        self._config = deepcopy(initial_config)
        self._update_config(initial_config)

    def get_config(self) -> dict:
        return deepcopy(self._config)

    @staticmethod
    def read_config_part(path: str) -> dict:
        if not path:
            return {}
        with open(path, 'r', encoding='utf8') as fd:
            return yaml.safe_load(fd)

    def read_config(self) -> dict:
        config_part = self.read_config_part(self._config_path())
        self._update_config(config_part)
        return self.get_config()

    def _update_config(self, new_config: dict):
        self._config.update(new_config)

    def _config_path(self) -> str:
        return os.getenv('CONFIG_PATH', '')

