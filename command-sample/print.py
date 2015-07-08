#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" print.py


"""

import sys
import json

def main():
    print("argv[1]: %s" % sys.argv[1])
    print("argv[2]: %s" % sys.argv[2])
    print(json.dumps(json.loads(sys.argv[2]), sort_keys=True, indent=2))

if __name__ == "__main__":
    main()
