#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" retry.py


"""

import json
import os
import sys

root_dir = os.path.abspath(os.path.dirname(__file__)) + "/"

def main():
    global root_dir

    filename = sys.argv[1]
    record_id = sys.argv[2]

    fp = open(filename)
    js = json.load(fp)
    fp.close()

    r = None
    j = None
    
    for d in js:
        if d["id"] == record_id:
            r = d["recorded"].encode("utf-8")
            j = json.dumps(d, ensure_ascii=False).encode("utf-8")

    os.system("python %s/enque.py '%s' '%s'" % (root_dir, r, j))

if __name__ == "__main__":
    main()
