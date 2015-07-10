#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" enque.py


"""

import fcntl
import json
import logging
import os
import sys
import time

root_dir = os.path.abspath(os.path.dirname(__file__)) + "/"
config = None

def load_config():
    global root_dir
    global config
    fp = open(root_dir + "config.json")
    config = json.load(fp)
    fp.close()

def init_logger():
    global config
    logging.basicConfig(
        filename=config["akane"]["metaFileDir"] + "/log-enque.txt",
        format='%(asctime)s: %(message)s',
        level=logging.INFO)
    
def get_queue_file():
    global config
    return config["akane"]["metaFileDir"] + "/queue.json"

def main():
    load_config()
    init_logger()

    logging.info("%s, %s" % (sys.argv[1], sys.argv[2]))
    added = json.loads(sys.argv[2])
    queue_file = get_queue_file()
    
    fp = None
    for i in range(5):
        try:
            fp = open(queue_file, 'rw+')
            fcntl.flock(fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            logging.info("queue lock succeeded.")
            break
        except IOError as e:
            logging.info("wait... (%s)" % str(e))
            time.sleep(2 ** (i + 3))
    if fp is None:
        logging.info("queue lock succeeded.")
        return
    
    js = json.load(fp)
    js.append(added)
    
    fp.truncate(0)
    fp.seek(0)
    fp.write(json.dumps(js, ensure_ascii=False).encode("utf-8"))
    fp.close()

if __name__ == "__main__":
    main()
