#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" stash.py


"""

import fcntl
import json
import os
import sys

def main():
    filename = sys.argv[1]
    fp = None
    try:
        fp = open(filename, 'rw+')
        fcntl.flock(fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except Exception as e:
        print(e)
        sys.exit(1)

    js = json.load(fp)

    data = filter(
        lambda item:(os.path.exists(item['recorded']) or
                     os.path.exists(item['encoded'])),
        js)

    fp.truncate(0)
    fp.seek(0)
    fp.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    
    fp.close()

if __name__ == "__main__":
    main()
