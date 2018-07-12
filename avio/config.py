import os
import yaml
from copy import deepcopy


class ConfigParser:

    def __init__(self, initial_config: dict = None):
        if not initial_config:
            initial_config = {}
        self._default_config = deepcopy(initial_config)
        self._config = deepcopy(initial_config)
        self.update_config(initial_config)

    def get_config(self) -> dict:
        return deepcopy(self._config)

    def read_config(self) -> dict:
        """
        Updates local config with yaml.
        """
        config_part = self._read_config_file(self._config_path())
        self.update_config(config_part)
        return self.get_config()

    def update_config(self, new_config: dict):
        """
        Updates local config with new config
        """
        self._config = self.update(self._config, new_config)

    @staticmethod
    def update(old_config, new_config) -> dict:
        if not new_config:
            new_config = {}
        config = deepcopy(old_config)
        # Much like config.update(new_config), but update 2nd level dicts, instead of replacing
        for key, value in new_config.items():
            if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                config[key].update(value)
            else:
                config[key] = value
        return config

    @staticmethod
    def _read_config_file(path: str) -> dict:
        if not path:
            return {}
        with open(path, 'r', encoding='utf8') as fd:
            cfg = yaml.safe_load(fd)
        return cfg or {}

    def _config_path(self) -> str:
        return os.getenv('CONFIG_PATH', '')
