#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" dispatcher.py


"""

import datetime
import json
import logging
import os
import sys

root_dir = os.path.abspath(os.path.dirname(__FILE__)) + "/"
config = None
logger = None

def main():
    global config
    load_config()

    if config["logging"]:
        init_logger(config["logFile"])

    if is_recording():
        log("chinachu is recording. exit.")
        sys.exit(1)

    if is_processing():
        log("akane is processing previous task. exit.")
        sys.exit(2)
    

def load_config():
    """ このファイルと同じフォルダの config.jsonを読み込む """
    global config
    global root_dir
    fp = open(root_dir + "config.json")
    config = json.load(fp)
    fp.close()

def init_logger(logFile):
    """ loggerを初期化 """
    global logger
    logger = logging.basicConfig(filename=logFile)

def log(msg, *args, **kwargs):
    """ loggerが有効な場合、logを出力する """
    global logger
    if logger is not None:
        logger.info(msg, *args, **kwargs)

if __name__ == "__main__":
    main()
