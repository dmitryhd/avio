import os
import contextlib

import pytest

import avio.config as config


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
    result_config = config.read_yaml(config_file)
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
        result_config = config.get_config_from_env()
    assert config_content == result_config


@pytest.mark.skip
def test_config_from_not_existing_env():
    with pytest.raises(FileNotFoundError):
        with set_env_var('CONFIG_PATH', 'not_existing_file.yaml'):
            config.get_config_from_env()


@contextlib.contextmanager
def del_env_var(key):
    original_value = os.getenv(key)
    try:
        del os.environ[key]
    except KeyError:
        pass
    yield
    if original_value is None:
        del os.environ[key]
    else:
        os.environ[key] = str(original_value)


@pytest.mark.skip
def test_config_without_env():
    with del_env_var('CONFIG_PATH'):
        assert {} == config.get_config_from_env()
