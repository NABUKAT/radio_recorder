# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, timezone
import requests
from requests.exceptions import Timeout
import os, sys
import time
import base64
import subprocess

class Authorization(object):
    """Radiko APIの認可クラス"""
    _AUTH1_URL = 'https://radiko.jp/v2/api/auth1'
    _AUTH2_URL = 'https://radiko.jp/v2/api/auth2'

    _RADIKO_AUTH_KEY = b'bcd151073c03b352e1ef2fd66c32209da9ca0afa'    # radiko apiの仕様で決まっている値 ref http://radiko.jp/apps/js/playerCommon.js

    def __init__(self):
        # RadikoAPIの仕様でheaderのX-Radiko-***の項目は必須
        self._headers = {
            'User-Agent': 'python3.7',
            'Accept': '*/*',
            'X-Radiko-App': 'pc_html5',
            'X-Radiko-App-Version': '0.0.1',
            'X-Radiko-User': 'dummy_user',
            'X-Radiko-Device': 'pc',
            'X-Radiko-AuthToken': '',
            'X-Radiko-Partialkey': '',
            'X-Radiko-AreaId': os.getenv('RADIKO_AREA_ID')
        }
        self._auth()

    def get_auththenticated_headers(self):
        """認可済みのhttp headerを返す"""
        return self._headers

    def _auth(self):
        """RadikoAPIで認可する"""
        # 認可トークンとauth2で必要なpartialkey生成に必要な値を取得する
        res = self._call_auth_api(Authorization._AUTH1_URL)
        self._headers['X-Radiko-AuthToken'] = self._get_auth_token(res)
        self._headers['X-Radiko-Partialkey'] = self._get_partial_key(res)
        res = self._call_auth_api(Authorization._AUTH2_URL)

    def _call_auth_api(self, api_url):
        """Radikoの認可APIを呼ぶ"""
        try:
            res = requests.get(url=api_url, headers=self._headers, timeout=5.0)
        except Timeout as e:
            raise Exception(f'failed in {api_url}.')
        if res.status_code != 200:
            raise Exception(f'failed in {api_url}.')
        return res

    def _get_auth_token(self, response):
        """HTTPレスポンスから認可トークンを取得する"""
        return response.headers['X-Radiko-AUTHTOKEN']

    def _get_partial_key(self, response):
        """
        HTTPレスポンスから認可用partial keyを取得する
        アルゴリズムはhttp://radiko.jp/apps/js/radikoJSPlayer.js createPartialkey関数を参照している。
        """
        length = int(response.headers['X-Radiko-KeyLength'])
        offset = int(response.headers['X-Radiko-KeyOffset'])
        partial_key = base64.b64encode(Authorization._RADIKO_AUTH_KEY[offset: offset + length])
        return partial_key

class Radiko(object):
    def __init__(self, station):
        self._headers = self._make_headers()
        self._station = station

    def _make_headers(self):
        """HTTPリクエストのヘッダーを作成する"""
        headers = Authorization().get_auththenticated_headers()
        headers['Connection']='keep-alive'
        return headers

    def play(self):
        """再生する"""
        url = f'http://f-radiko.smartstream.ne.jp/{self._station}/_definst_/simul-stream.stream/playlist.m3u8'
        subprocess.Popen(f"ffplay -nodisp -loglevel quiet -headers 'X-Radiko-Authtoken:{self._headers['X-Radiko-AuthToken']}' -i '{url}'", shell=True, stdin=subprocess.PIPE)

    def record(self, filepath, rtime):
        """録音する"""
        url = f'http://f-radiko.smartstream.ne.jp/{self._station}/_definst_/simul-stream.stream/playlist.m3u8'
        subprocess.Popen(f"ffmpeg -headers 'X-Radiko-Authtoken:{self._headers['X-Radiko-AuthToken']}' -i '{url}' -vn {filepath}", shell=True, stdin=subprocess.PIPE)
        end = datetime.now() + timedelta(minutes=rtime)
        while(datetime.now() <= end):
            time.sleep(1.0)
        com = "q"
        pid = subprocess.Popen("ps aux | grep -v grep | grep 'ffmpeg' | awk '{print $2}'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        pid = str(pid, "utf-8").splitlines()
        for p in pid:
            print(os.path.join("/proc", p, "fd", "0"))
            with open(os.path.join("/proc", p, "fd", "0"), "w") as s:
                s.write(com)
            break

def logging(str):
    datestr = datetime.now().strftime("%Y%m%d")
    f = open("/tmp/radikopy" + datestr + ".log", "a")
    f.write(str + "\n")
    f.close()

def play(station):
    # 再生を実施する
    radiko = Radiko(station)
    radiko.play()

def record(station, rtime, outfilename):
    # 録音を実施する
    radiko = Radiko(station)
    radiko.record(outfilename, rtime)

if __name__ == '__main__':
    #play("FMAICHI")
    #record("FMAICHI", 3, "test.aac")
    if sys.argv[1] == "play":
        play(sys.argv[2])
    elif sys.argv[1] == "record":
        record(sys.argv[2], int(sys.argv[3]), sys.argv[4])
