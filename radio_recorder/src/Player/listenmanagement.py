# -*- coding: utf-8 -*-
import os
import glob
import json

class ListenManagement:
    def __init__(self, managefile="/home/pi/RadikoPlayer/lm.txt", basedir="/media/radiko"):
        self.managefile = managefile
        if os.path.exists(managefile):
            # lm.txtがある場合
            f = open(self.managefile, "r")
            self.lm = json.load(f)
            f.close()
            # lm.txtを最新の状態にする
            tmp = []
            bdlist = glob.glob(basedir + "/*")
            for bd in bdlist:
                # ディレクトリに新規追加されていたら管理対象とする
                fs = glob.glob(bd + "/*")
                for f in fs:
                    if f not in self.lm:
                        self.lm[f] = False
                    tmp.append(f)
            # ディレクトリにない場合は管理から外す
            tmp2 = []
            for lm in self.lm:
                if lm not in tmp:
                    tmp2.append(lm)
            for t in tmp2:
                self.lm.pop(t)
            # ファイル保存
            jd = json.dumps(self.lm, ensure_ascii=False)
            f = open(self.managefile, "w")
            f.write(jd)
            f.close()
        else:
            # lm.txtがない場合
            self.lm = {}
            bdlist = glob.glob(basedir + "/*")
            for bd in bdlist:
                fs = glob.glob(bd + "/*")
                for f in fs:
                    self.lm[f] = False
            # ファイル保存
            jd = json.dumps(self.lm, ensure_ascii=False)
            f = open(self.managefile, "w")
            f.write(jd)
            f.close()
    
    # 既聴更新機能
    def update(self, path):
        self.lm[path] = True
        # ファイル保存
        jd = json.dumps(self.lm, ensure_ascii=False)
        f = open(self.managefile, "w")
        f.write(jd)
        f.close()

    # 管理データリスト取得機能
    def get(self):
        return self.lm

if __name__ == "__main__":
    lm = ListenManagement()
    lm.update("/media/radiko/伊集院光の深夜の馬鹿力/20190409_伊集院光の深夜の馬鹿力.m4a")