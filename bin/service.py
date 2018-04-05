#!/usr/bin/env python3

import os.path as path
import sys


def main():
    cur_dir = path.dirname(path.abspath(__file__))
    sys.path.append(path.join(cur_dir, '..'))
    import avio.application
    app = avio.application.make_app()
    avio.application.run_app(app)


if __name__ == '__main__':
    main()
