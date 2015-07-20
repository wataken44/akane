#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" select.py


"""

import json
import sys

def main():
    filename = sys.argv[1]
    record_id = sys.argv[2]

    fp = open(filename)
    js = json.load(fp)
    fp.close()

    for d in js:
        if d["id"] == record_id:
            print(json.dumps(d, ensure_ascii=False).encode("utf-8"))

if __name__ == "__main__":
    main()
