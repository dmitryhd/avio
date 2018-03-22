#!/usr/bin/env python3

import os.path as path
import sys

if __name__ == '__main__':
    cur_dir = path.dirname(path.abspath(__file__))
    sys.path.append(path.join(cur_dir, '..'))
    import avio.application
    app = avio.application.make_app()
    avio.application.run_app(app)