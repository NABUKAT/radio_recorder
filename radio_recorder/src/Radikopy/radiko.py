# -*- coding: utf-8 -*-

# pip3 install ffmpeg-python
# pip3 install m3u8

from datetime import datetime, timedelta, timezone
import requests
from requests.exceptions import Timeout
import os, sys, re
import time
import logging
import urllib.request, urllib.error, urllib.parse
import base64

import ffmpeg
import m3u8

JST = timezone(timedelta(hours=+9), 'JST')

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
        logging.debug(f'authenticated headers:{self._headers}')
        logging.debug(f'res.headers:{res.headers}')
        for c in res.cookies:
            logging.debug(f'res.cookie:{c}')
        logging.debug(f'res.content:{res.content}')

    def _call_auth_api(self, api_url):
        """Radikoの認可APIを呼ぶ"""
        try:
            res = requests.get(url=api_url, headers=self._headers, timeout=5.0)
        except Timeout as e:
            logging.warning(f'failed in {api_url}.')
            logging.warning('API Timeout')
            logging.warning(e)
            raise Exception(f'failed in {api_url}.')
        if res.status_code != 200:
            logging.warning(f'failed in {api_url}.')
            logging.warning(f'status_code:{res.status_code}')
            logging.warning(f'content:{res.content}')
            raise Exception(f'failed in {api_url}.')
        logging.debug(f'auth in {api_url} is success.')
        return res

    def _get_auth_token(self, response):
        """HTTPレスポンスから認可トークンを取得する"""
        return response.headers['X-Radiko-AUTHTOKEN']

    def _get_partial_key(self, response):
        """HTTPレスポンスから認可用partial keyを取得する

        アルゴリズムはhttp://radiko.jp/apps/js/radikoJSPlayer.js createPartialkey関数を参照している。
        """
        length = int(response.headers['X-Radiko-KeyLength'])
        offset = int(response.headers['X-Radiko-KeyOffset'])
        partial_key = base64.b64encode(Authorization._RADIKO_AUTH_KEY[offset: offset + length])
        return partial_key

class Radiko(object):
    """Radikoクラス"""

    _MASTER_PLAYLIST_BASE_URL = 'https://rpaa.smartstream.ne.jp/so/playlist.m3u8'
    _DUMMY_LSID = '11111111111111111111111111111111111111' # Radiko APIの仕様で38桁の文字列が必要。

    def __init__(self, station):
        self._headers = self._make_headers()
        self._station = station

    def _make_headers(self):
        """HTTPリクエストのヘッダーを作成する"""
        headers = Authorization().get_auththenticated_headers()
        headers['Connection']='keep-alive'
        logging.debug(f'headers: {headers}')
        return headers

    def _make_master_playlist_url(self):
        """master playlistのURLを作成する"""
        url = f'{Radiko._MASTER_PLAYLIST_BASE_URL}?station_id={self._station}&l=15&lsid={Radiko._DUMMY_LSID}&type=b'
        logging.debug(f'playlist url:{url}')
        return url

    def _make_audio_headers(self):
        """音声取得用HTTPリクエストのヘッダーを作成する
        requests用のhttpヘッダーをもとにffmpeg用に文字列のHTTPリクエストヘッダーを作る。
        """
        header_list = [f'{k}: {v}'for k, v in self._headers.items()]
        audio_headers = '\r\n'.join(header_list)+'\r\n'
        logging.debug(f'audio headers: {audio_headers}')
        return audio_headers

    def _get_media_playlist_url(self):
        """media playlistのURLを取得する"""
        u = self._make_master_playlist_url()
        r = requests.get(url=u, headers=self._headers)
        if r.status_code != 200:
            logging.warning('failed to get media playlist url')
            logging.warning(f'status_code:{r.status_code}')
            logging.warning(f'content:{r.content}')
            raise Exception('failed in radiko get media playlist')
        m3u8_obj = m3u8.loads(r.content.decode('utf-8'))
        media_playlist_url = m3u8_obj.playlists[0].uri
        logging.debug(f'media_playlist_url: {media_playlist_url}')
        return media_playlist_url

    def _get_media_url(self, media_playlist_url):
        """音声ファイルのURLをmedia playlistから取得する"""
        query_time = int(datetime.now(tz=JST).timestamp() * 100)
        r = requests.get(url=f'{media_playlist_url}&_={query_time}',headers=self._headers)
        logging.debug(f'aac url:{media_playlist_url}&_={query_time}')
        if r.status_code != 200:
            return None
        m3u8_obj = m3u8.loads(str(r.content.decode('utf-8')))
        return [(s.program_date_time, s.uri) for s in m3u8_obj.segments]

    def _gen_temp_chunk_m3u8_url(self, url, auth_token ):
        headers =  {
            "X-Radiko-AuthToken": auth_token,
        }
        req  = urllib.request.Request( url, None, headers  )
        res  = urllib.request.urlopen(req)
        body = res.read().decode()
        lines = re.findall( '^https?://.+m3u8$' , body, flags=(re.MULTILINE) )
        # embed()
        return lines[0]

    def play(self):
        """再生する"""
        logging.debug('play start')
        url = f'http://f-radiko.smartstream.ne.jp/{self._station}/_definst_/simul-stream.stream/playlist.m3u8'
        m3u8 = self._gen_temp_chunk_m3u8_url(url, self._headers['X-Radiko-AuthToken'])
        os.system( f"ffplay -nodisp -loglevel quiet -headers 'X-Radiko-Authtoken:{self._headers['X-Radiko-AuthToken']}' -i '{url}'")

    def record(self, rtime):
        """録音する"""
        logging.debug('record start')
        media_playlist_url = self._get_media_playlist_url()
        end = datetime.now() + timedelta(minutes=rtime)
        recorded = set()
        while(datetime.now() <= end):
            url_list = self._get_media_url(media_playlist_url)
            if url_list == None:
                # 時間をおいてリトライすると取れるときがあるため待つ
                time.sleep(3.0)
                continue
            headers = self._make_audio_headers()
            # m3u8ファイルに記述されている音声ファイルを重複しないように取得する
            for dt, url in url_list:
                if dt in recorded:
                    continue
                if not os.path.isdir('/tmp/tmp'):
                    os.mkdir('/tmp/tmp')
                try:
                    ffmpeg\
                    .input(filename=url, f='aac', headers=headers)\
                    .output(filename=f'/tmp/tmp/{dt}.aac')\
                    .run(capture_stdout=True)
                except Exception as e:
                    logging.warning('failed in run ffmpeg')
                    logging.warning(e)
                recorded.add(dt)
            time.sleep(5.0)
        logging.debug('record end')
        return recorded

def play(station):
    # 再生を実施する
    radiko = Radiko(station)
    radiko.play()

def record(station, rtime, outfilename):
    # 録音を実施する
    radiko = Radiko(station)
    recorded = radiko.record(rtime)
    # 音声ファイルを一つに
    l = sorted(recorded)
    files = [f'/tmp/tmp/{e}.aac' for e in l]
    try:
        streams = [ffmpeg.input(filename=f) for f in files]
        ffmpeg\
            .concat(*streams,a=1,v=0)\
            .output(filename=outfilename, absf='aac_adtstoasc')\
            .run(capture_stdout=True)
    except Exception as e:
        logging.warning('failed in run ffmpeg concat')
        logging.warning(e)
    for f in files:
        os.remove(f)

if __name__ == '__main__':
    #play("FMAICHI")
    #record("FMAICHI", 3, "test.aac")
    if sys.argv[1] == "play":
        play(sys.argv[2])
    elif sys.argv[1] == "record":
        record(sys.argv[2], int(sys.argv[3]), sys.argv[4])