#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" enque.py


"""

import fcntl
import json
import os
import sys
import time

root_dir = os.path.abspath(os.path.dirname(__file__)) + "/"

def get_queue_file():
    global root_dir
    fp = open(root_dir + "config.json")
    js = json.load(fp)
    fp.close()
    return js["akane"]["metaDataDir"] + "/queue.json"

def main():
    added = json.loads(sys.argv[2])
    queue_file = get_queue_file()
    
    fp = None
    for i in range(5):
        try:
            fp = open(queue_file, 'rw+')
            fcntl.flock(fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except:
            time.sleep(2 ** (i + 3))
    # todo need logging...
    if fp is None:
        return

    js = json.load(fp)
    js.append(added)
    
    fp.truncate(0)
    fp.seek(0)
    fp.write(json.dumps(js, ensure_ascii=False).encode("utf-8"))
    fp.close()

if __name__ == "__main__":
    main()
