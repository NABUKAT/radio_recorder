# -*- coding: utf-8 -*-
from wsgiref import simple_server
from socketserver import ThreadingMixIn
from wsgiref.simple_server import WSGIServer
import json
from bottle import route, run, template, request, view, default_app, static_file
import os.path
import subprocess
from myomxplayer import MyOmxplayer
from dirtojson import dirToListJson
from prefecture2stations import Prefecture2Stations
from recordersetting import RecSetting
from recordersetting import RecorderSetting
from listenmanagement import ListenManagement

class ThreadedWSGIServer(ThreadingMixIn, WSGIServer):
    """マルチスレッド化した WSGIServer"""
    pass

base_path = "/media/radiko/"
setting_dir = "/home/pi/RadikoRecorder/setting/"
schedule_file = "/etc/cron.d/radiko_schedule"

# メイン
@route('/')
@view('index')
def index():
    pass

# スタティックファイル
@route('/static/css/<filename:path>')
def css(filename):
    return static_file(filename, root="static/css")

@route('/static/js/<filename:path>')
def js(filename):
    return static_file(filename, root="static/js")

@route('/static/img/<filename:path>')
def img(filename):
    return static_file(filename, root="static/img")

# 再生
@route('/playradiko')
@view('playradiko')
def playradiko():
    # コマンドの読み込み
    com = request.query.com
    if com == "":
        pass
    elif com == "stationlist":
        p2s = Prefecture2Stations(request.query.p)
        return [p2s.encode('utf-8')]
    elif com == "play":
        subprocess.Popen('/home/pi/RadikoPlayer/playradiko.sh stop', shell=True)
        subprocess.Popen('/home/pi/RadikoPlayer/playradiko.sh start ' + request.query.ch, shell=True)
        return [b"play"]
    elif com == "stop":
        subprocess.Popen('/home/pi/RadikoPlayer/playradiko.sh stop', shell=True)
        return [b"stop"]
    else:
        return [b"ng"]

# 録音ラジオプレイヤー
@route('/recradiko')
@view('recradiko')
def recradiko():
    # コマンドの読み込み
    com = request.query.com
    if com == "":
        pass
    elif com == "newplay":
        lm = ListenManagement()
        lm.update(request.query.path)
        mop = MyOmxplayer()
        mop.newplay(request.query.path)
        return [b"play"]
    elif com == "play":
        mop = MyOmxplayer()
        mop.play()
        return [b"play"]
    elif com == "pause":
        mop = MyOmxplayer()
        mop.pause()
        return [b"pause"]
    elif com == "stop":
        mop = MyOmxplayer()
        mop.stop()
        return [b"stop"]
    elif com == "p30":        
        mop = MyOmxplayer()
        mop.p30()
        return [b"play"]
    elif com == "p600":
        mop = MyOmxplayer()
        mop.p600()
        return [b"play"]
    elif com == "m30":
        mop = MyOmxplayer()
        mop.m30()
        return [b"play"]
    elif com == "m600":
        mop = MyOmxplayer()
        mop.m600()
        return [b"play"]
    elif com == "confirm":
        mop = MyOmxplayer()
        ret = mop.confirm()
        return [ret.encode('utf-8')]
    elif com == "list":
        if os.path.isfile(request.query.path):
            lm = ListenManagement()
            lm.update(request.query.path)
            mop = MyOmxplayer()
            mop.newplay(request.query.path)
            return [b"thisisfile"]
        else:
            list = dirToListJson(request.query.path)
            return [list.encode('utf-8')]

# 録音設定一覧
@route('/recradikoset')
@view('recradikoset')
def recradikoset():
    # コマンドの読み込み
    com = request.query.com
    if com == "":
        pass
    elif com == "listview":
        recset = RecorderSetting(setting_dir, schedule_file)
        return [json.dumps(recset.list(), ensure_ascii=False).encode("utf-8")]
    elif com == "delete":
        recset = RecorderSetting(setting_dir, schedule_file)
        recset.delete(request.query.sf)
        return [b"ok"]

# 録音設定追加
@route('/addpage')
@view('addpage')
def addpage():
    # コマンドの読み込み
    com = request.query.com
    if com == "":
        pass
    elif com == "stationlist":
        p2s = Prefecture2Stations(request.query.p)
        return [p2s.encode('utf-8')]
    elif com == "add":
        rs = RecSetting(request.query.ch, request.query.rt, request.query.name, request.query.dw, request.query.h, request.query.m)
        recset = RecorderSetting(setting_dir, schedule_file)
        recset.create(rs)
        return [b"ok"]

# 録音設定編集
@route('/editpage')
@view('editpage')
def editpage():
    # コマンドの読み込み
    com = request.query.com
    if com == "":
        sf = {"sf": request.query.sf}
        return sf
    elif com == "stationlist":
        p2s = Prefecture2Stations(request.query.p)
        return [p2s.encode('utf-8')]
    elif com == "editview":
        recset = RecorderSetting(setting_dir, schedule_file)
        list = recset.list()
        for l in list:
            if l["settingfile"] == request.query.sf:
                ret = l
                break
        return [json.dumps(ret, ensure_ascii=False).encode("utf-8")]
    elif com == "edit":
        rs = RecSetting(request.query.ch, request.query.rt, request.query.name, request.query.dw, request.query.h, request.query.m, settingfile=request.query.sf)
        recset = RecorderSetting(setting_dir, schedule_file)
        recset.edit(rs)
        return [b"ok"]

if __name__ == '__main__':
    server = simple_server.make_server('', 8123, default_app(), server_class=ThreadedWSGIServer)
    server.serve_forever()