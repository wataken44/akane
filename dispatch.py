#!/usr/bin/env python
# -*- coding: utf-8  python-indent-offset: 4 -*-

""" dispatcher.py


"""

import codecs
import datetime
import fcntl
import glob
import json
import logging
import os
import sys
import threading

try:
    from urllib.request import build_opener, HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler
except:
    from urllib2 import build_opener, HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler

root_dir = os.path.abspath(os.path.dirname(__file__)) + "/"

reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

class Dispatcher(object):
    def __init__(self):
        self._config = None
        self._logger = None

        self.load_config()

        if "log" in self._config["akane"]:
            self.init_logger()

        self._opener = None
        self.init_opener()
         
    def run(self):
        if self.is_recording():
            self.log("chinachu is recording. exit.")
            sys.exit(1)
            
        self.clean_defunct_task()

        processing_task_count = self.count_processing_task()
        max_processing_task_count = self._config["akane"]["maxProcessingTaskCount"]
        if processing_task_count >= max_processing_task_count:
            self.log("akane is processing previous tasks. exit.")
            sys.exit(2)
        self.dispatch_task(max_processing_task_count - processing_task_count)

    def load_config(self):
        """ このファイルと同じフォルダの config.jsonを読み込む """
        global root_dir
        fp = open(root_dir + "config.json")
        self._config = json.load(fp)
        fp.close()

    def init_logger(self):
        """ loggerを初期化 """
        logging.basicConfig(
            filename=self._config["akane"]["log"],
            format='%(asctime)s: %(message)s',
            level=logging.INFO)
        self._logger = True

    def log(self, msg, *args, **kwargs):
        """ loggerが有効な場合、logを出力する """
        if self._logger:
            logging.info(msg, *args, **kwargs)

    def init_opener(self):
        """ chinachuのAPIを実行するためのopenerを初期化する """
        pm = HTTPPasswordMgrWithDefaultRealm()
        url = self._config["chinachu"]["apiEndpoint"]
        user = self._config["chinachu"]["username"]
        password = self._config["chinachu"]["password"]
        pm.add_password(None, url, user, password)
        handler = HTTPBasicAuthHandler(pm)
        self._opener = build_opener(handler)
        
    def get_api(self, path):
        """ chinachuのAPIにアクセスする """
        url = self._config["chinachu"]["apiEndpoint"]
        if url[-1] != "/":
            url += "/"
        url += path
        fp = self._opener.open(url)
        js = json.load(fp)
        fp.close()
        return js

    def is_recording(self):
        """ chinachuが録画中か判断する """
        recording = self.get_api("recording.json")
        return len(recording) > 0

    def clean_defunct_task(self):
        """ 異常終了したtaskを消す """
        pattern = self._config["akane"]["lockFileDir"] + "/*.lock"
        files = glob.glob(pattern)
        for f in files:
            fn = f.encode('utf-8')
            fp = None
            defunct = False
            try:
                fp = open(fn, 'rw+')
                fcntl.flock(fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                # 通常taskは開始時にlockファイル生成し、終了時にlockファイル削除する
                # lockが取れる場合、異常終了している
                defunct = True
            except IOError:
                pass
            if fp is not None:
                fp.close()
            if defunct:
                os.remove(fn)

    def count_processing_task(self):
        """ 処理中のtaskの数を数える """
        pattern = self._config["akane"]["lockFileDir"] + "/*.lock"
        files = glob.glob(pattern)
        return len(files)

    def dispatch_task(self, count=1):
        """ taskを実行する """
        dispatchable_seconds = self.get_dispatchable_seconds()

        # queueをopen
        fp = None
        try:
            fn = self._config["akane"]["metaFileDir"] + "/queue.json"
            fp = open(fn, 'rw+')
            fcntl.flock(fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            self.log("akane cannot open queue file(maybe locked or not exist). exit.")
            sys.exit(3)

        # queueの先頭から、処理可能なtaskを選択
        # 選択されたtaskは取り除く
        task = []
        js = json.loads(fp.read())

        for i in range(count):
            for k in range(len(js)):
                if js[k]["seconds"] < dispatchable_seconds:
                    task.append(js.pop(k))
                    break

        # queueを更新する
        fp.truncate(0)
        fp.seek(0)
        fp.write(json.dumps(js, ensure_ascii=False).encode('utf-8'))
        fp.close()
        
        thread = []
        for t in task:
            thread.append(threading.Thread(target=self.process_task, args=(t,)))

        for th in thread:
            th.start()

        for th in thread:
            th.join()
        
    def get_dispatchable_seconds(self):
        """ 次の録画開始時間までに処理可能な録画済みの動画の長さを返す """
        next_recording_start = self.get_next_recording_start()
        if next_recording_start is None:
            # 録画がないときは1週間 
            return 7 * 24 * 60 * 60

        s = datetime.datetime.utcfromtimestamp(next_recording_start)
        n = datetime.datetime.utcnow()
        dd = (s - n)
        d = dd.days * 24 * 60 + dd.seconds

        r = self._config["akane"]["processTimeRatio"]
        c = self._config["akane"]["processTimeConstant"]

        self.log("next = %s, now = %s, delta = %d, dispatable = %f" % (str(s), str(n), d, (d - c)/r))
        
        return (d - c) / r
        
    def get_next_recording_start(self):
        """ 次の録画開始時間を返す """
        reserves = self.get_api("reserves.json")

        # 次の録画開始時間, unixtime
        start = None
        if len(reserves) > 0:
            start = reserves[0]["start"] 
            for r in reserves:
                start = min(start, r["start"])
        else:
            return None    
        return start / 1000

    def process_task(self, task):
        task_id = task["id"]
        title = task["fullTitle"]
        recorded = task["recorded"]
        lock = self._config["akane"]["lockFileDir"] + "/" + os.path.basename(recorded) + ".lock"
        
        recorded = recorded.encode('utf-8')
        lock = lock.encode('utf-8')

        fp = None
        try:
            if os.path.exists(lock):
                fp = open(lock, 'rw+')
            else:
                fp = open(lock, 'w+')
            fcntl.flock(fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError as e:
            self.log("cannot get lock: %s" % str(e))
            return
        
        self.log("start: (%s, %s, %s)" % (task_id, title, recorded))

        for command in self._config["akane"]["processCommands"]:
            c = "%s '%s' '%s'" % (command, recorded, json.dumps(task, ensure_ascii=False).encode('utf-8'))
            self.log("command: %s" % c)
            os.system(c)
        
        self.log("end: (%s, %s, %s)" % (task_id, title, recorded))
        fp.close()

def main():
    dispatcher = Dispatcher()
    dispatcher.run()
        
if __name__ == "__main__":
    main()
