#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" encode.py


"""

import fcntl
import json
import logging
import os
import sys
import time

config = None
root_dir = os.path.abspath(os.path.dirname(__file__)) + "/"

def load_config():
    global config
    global root_dir

    fp = open(root_dir + "encode-config.json")
    config = json.load(fp)
    fp.close()
    
def main():
    global config
    load_config()

    logging.basicConfig(
        filename=config["log"],
        format='%(asctime)s: %(message)s',
        level=logging.INFO)

    recorded_info = json.loads(sys.argv[2])
    recorded_file = recorded_info["recorded"]
    basename = os.path.basename(recorded_file)

    command_template = config["command"]
    encoded_dir = config["encodedDir"]
    encoded_ext = config["encodedExt"]
    encoded_file = encoded_dir + '/' + os.path.splitext(basename)[0] + encoded_ext

    command = command_template.replace("<recorded>", recorded_file)
    command = command.replace("<encoded>", encoded_file)
    
    logging.info("start: %s" % command)
    os.system(command.encode("utf-8"))
    logging.info("end: %s" % command)
    
    encoded_info_file = config["encodedInfoFile"]
    fp = None
    for i in range(5):
        try:
            fp = open(encoded_info_file, 'rw+')
            fcntl.flock(fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except IOError:
            time.sleep(2 ** i)
    if fp is None:
        logging.error("[ERROR] cannot get lock for %s, %s" % (sys.argv[1], sys.argv[2]))
        sys.exit(1)

    encoded_info = json.load(fp)
    recorded_info["encoded"] = encoded_file
    recorded_info["encodedCommand"] = command

    encoded_info.append(recorded_info)
    fp.truncate(0)
    fp.seek(0)
    fp.write(json.dumps(encoded_info, ensure_ascii=False).encode("utf-8"))
    fp.close()

if __name__ == "__main__":
    main()
