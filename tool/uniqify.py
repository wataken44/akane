#!/usr/bin/env python


import json
import sys

def main():
    fp = open(sys.argv[1])
    js = json.load(fp)
    fp.close()

    j = 0
    while j != len(js):
        dup = False
        for k in range(j+1, len(js)):
            if js[j]["id"] == js[k]["id"]:
                dup = True
        if dup:
            js.pop(j)
            print("delete %d" % j)
        else:
            j += 1

    fp = open(sys.argv[1], "w")
    fp.write(json.dumps(js, ensure_ascii=False).encode('utf-8'))
    fp.close()

if __name__ == "__main__":
    main()
