import os
import contextlib

import pytest

from avio.config import ConfigParser


@pytest.fixture()
def config_file(tmpdir):
    file = tmpdir.join('cfg.yaml')
    document = '''
      a: 1
      b:
        c: str1
        d: [st1, st2]
    '''
    file.write(document)
    return file


@pytest.fixture()
def config_content():
    return {
        'a': 1,
        'b': {
            'c': 'str1',
            'd': ['st1', 'st2'],
        }
    }


def test_read_yaml(config_file, config_content):
    result_config = ConfigParser.read_config_part(config_file)
    assert config_content == result_config


@contextlib.contextmanager
def set_env_var(key, value):
    original_value = os.getenv(key)
    os.environ[key] = str(value)
    yield
    if original_value is None:
        del os.environ[key]
    else:
        os.environ[key] = str(original_value)


def test_config_from_env(config_file, config_content):
    with set_env_var('CONFIG_PATH', str(config_file)):
        result_config = ConfigParser().read_config()
    assert config_content == result_config


@pytest.fixture()
def default_config():
    return {
        'int_opt': 1,
        'float_opt': 0.1,
        'str_opt': 'st',
        'list_opt': [1, 2],
        'dict_opt': {
            'a': 'b',
            'c': 'd',
        }
    }

def test_config_parser():
    conf_parser = ConfigParser(default_config())
    assert default_config() == conf_parser.get_config()
