#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" dump.py


"""

import json
import os
import sys

def main():
    fp = open(sys.argv[1])
    js = json.load(fp, encoding="utf-8")
    s = json.dumps(js, indent=2, ensure_ascii=False)
    print(s.encode('utf-8'))
    fp.close()


if __name__ == "__main__":
    main()
