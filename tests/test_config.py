import avio.config as config


def test_read_yaml(tmpdir):
    file = tmpdir.join('cfg.yaml')
    document = '''
      a: 1
      b:
        c: str1
        d: [st1, st2]
    '''
    file.write(document)
    result_config = config.read_yaml(file)
    expected_config = {
        'a': 1,
        'b': {
            'c': 'str1',
            'd': ['st1', 'st2'],
        }
    }
    assert expected_config == result_config
