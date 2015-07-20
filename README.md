akane (supplemental tool for chinachu)

### 背景

[Chinachu](https://github.com/kanreisa/Chinachu) を利用して録画を行うと、recordedCommandで録画後に実行するコマンドが指定できる。[(参考)](https://github.com/kanreisa/Chinachu/wiki/Configuration-recordedCommand)

しかし、recordedCommandでエンコードなどの時間がかかる処理をしようとすると、後続の録画や、実行中の処理のことを考慮せずに処理が実施される。たとえばTurion N54L(HP MicroServerのCPU)で2passエンコードを行おうとすると録画時間の4倍の時間がかかる。録画4つとエンコード4つが重複したりするのはHDDに高負荷をかけると考えられるのでなるべく避けたい。

そのため、録画終了後にいったんqueueに入れ、処理時間が次の録画の開始前に終わるようなら処理を実行する。

### 設定

#### install

```
$ cd /some/directory/
$ git clone https://github.com/wataken44/akane
```

#### chinachuのconfig.json

enque用のコマンドを登録する

```
  "recordedCommand": "/some/directory/akane/enque.py"
```

#### akaneのconfig.json

```
$ cd /some/directory/akane
$ cp config-sample.json config.json
$ vi config.json
```

設定項目の意味
```
{
  "chinachu": {
    "apiEndpoint": "chinachuのAPIのURL (例: http://localhost/api/)",
    "username": "chinachuのbasic認証のユーザ名(例: akane)",
    "password": "chinachuのbasic認証のパスワード(例: bakuhatsu)"
  },
  "akane": {
    "log": "ログファイル(例: /some/directory/log.txt)",
    "lockFileDir": "lockを置くdirectory(例: /some/directory/tmp/)",
    "metaFileDir": "metaFileを置くdirectory(例: /some/directory/meta/)",
    "maxProcessingTaskCount": 並列に実行するtask数(例: 1),
    "processCommands": ["実行するcommand(例: /home/chinachu/akane/command-sample/encode.py"],
    "processTimeRatio": processCommandsで指定したcommandを実行するのにかかる時間を見積もるときの、録画されたファイルの時間に対する係数(例: 5.5),
    "processTimeConstant": processCommandsで指定したcommandを実行するのにかかる時間を見積もるときの定数項(例: 400)
  }
}
```

queueの初期化
```
$ echo '[]' > <metaFileDir>/queue.json
```

補足
* lockFileDir, metaFileDirは手動で作成要。slashで終わらなければいけない。
* 録画された動画を処理する条件は (次の予約までの時間[秒]) > processTimeRatio * (動画の長さ[秒]) + processTimeConstant
* processCommandsの各コマンドには、chinachuのrecordedCommandと同じ引数が渡される($1がファイル名、$2がjson)。

#### encode.pyのencode-config.json(利用する場合)

```
$ cd /some/directory/akane/command-sample
$ cp encode-config-sample.json encode-config.json
$ vi encode-config.json
```

設定例
```
{
  "log": "ログファイル(例: /mnt/data_01/meta/log-encode.txt)",
  "encodedDir": "出力directory(例: /mnt/data_01/mp4)",
  "encodedExt": "出力拡張子(例: .mp4)",
  "encodedInfoFile": "/mnt/data_01/meta/encoded.json",
  "command": "/home/chinachu/Chinachu/usr/bin/ffmpeg -y -i '<recorded>' -f mp4 -vcodec libx264 -fpre /mnt/data_01/etc/libx264-hq-ts.ffpreset -r 30000/1001 -aspect 16:9 -s 1280x720 -b:v 1800000 -minrate 1800000 -pass 1 -an -movflags faststart '<encoded>' 2>&1 > /mnt/data_01/meta/log-ffmpeg.txt && /home/chinachu/Chinachu/usr/bin/ffmpeg -y -i '<recorded>' -f mp4 -vcodec libx264 -fpre /mnt/data_01/etc/libx264-hq-ts.ffpreset -r 30000/1001 -aspect 16:9 -s 1280x720 -bufsize 20000k -b:v 1800000 -minrate 1800000 -pass 2 -movflags faststart '<encoded>' 2>&1 >> /mnt/data_01/meta/log-ffmpeg.txt"
}
```

補足
* commandの&lt;recorded&gt;は録画されたファイルのフルパス、&lt;encoded&gt;は &lt;encodedDir&gt;/&lt;録画されたファイルのbasename&gt;&lt;encodedExt&gt; に置換される

#### cronの設定

設定例
```
16,46  *  *  *  *  cd /mnt/data_01/tmp/; /usr/bin/env python /home/chinachu/akane/dispatch.py > /dev/null
```
