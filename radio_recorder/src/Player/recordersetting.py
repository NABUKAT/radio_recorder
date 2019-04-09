# -*- coding: utf-8 -*-
from pathlib import Path
import json
import shutil
import os
import glob

class RecSetting:
    # dayofweek⇒ 0:日曜～6:土曜
    def __init__(self, channel, rectime, name, dayofweek, hour, minute, savenum=8, settingfile=""):
        self.channel = channel
        self.rectime = rectime
        self.name = name
        self.schedule = []
        self.schedule.append(str(minute))
        self.schedule.append(str(hour))
        self.schedule.append("*")
        self.schedule.append("*")
        self.schedule.append(str(dayofweek))
        self.schedule.append("root")
        self.schedule.append("/home/pi/RadikoRecorder/bin/rec_set.sh")
        self.savenum = savenum
        self.settingfile = settingfile
        self.dp = {}
        self.dp["channel"] = self.channel
        self.dp["rectime"] = self.rectime
        self.dp["name"] = self.name
        self.dp["schedule"] = self.schedule
        self.dp["settingfile"] = self.settingfile
        self.dp["savenum"] = self.savenum

    def getObject(self):
        return self.dp

    def getJsonStr(self):
        return json.dumps(self.dp, ensure_ascii=False)

    def __repr__(self):
        return self.getJsonStr()

class RecorderSetting:
    # コンストラクタ
    def __init__(self, setting_dir, schedule_file, save_dir="/media/radiko/"):
        self.setting_dir = setting_dir
        self.schedule_file = schedule_file
        self.save_dir = save_dir

        # 設定ファイルの読み込み
        self.rec_set = self.__setting2object()

        # スケジュールファイルの読み込み
        self.schedule = self.__schedule2object()

    # 設定ファイルを読み込む
    def __setting2object(self):
        # 設定ファイルの読み込み
        p = Path(self.setting_dir)
        settings = list(p.glob("rec_set*.prm"))
        rec = []
        for setting in settings:
            f = open(str(setting), "r", encoding="utf-8")
            tmp = f.read()
            f.close()
            ret = {}
            tmps = tmp.splitlines()
            for t in tmps:
                if "maxsavefilenum=" in t:
                    ts = t.split("=")
                    ret["savenum"] = int(ts[1])
                elif "channel=" in t:
                    ts = t.split("=")
                    ret["channel"] = ts[1]
                elif "rectime=" in t:
                    ts = t.split("=")
                    ret["rectime"] = int(ts[1])
                elif "filename=" in t:
                    ts = t.split("=")
                    ret["name"] = ts[1]
            ret["settingfile"] = str(setting.name)
            rec.append(ret)
        return rec

    # 設定ファイルに書き込む
    def __object2setting(self):
        for obj in self.rec_set:
            lines = []
            lines.append("#--------------------#")
            lines.append("\n#   パラメータ設定   #")
            lines.append("\n#--------------------#")
            lines.append("\n\n# 保存フォルダ")
            lines.append("\nsavefolder=" + self.save_dir + obj["name"] + "/")
            lines.append("\n\n# 最大保存数（古いファイルから削除する）")
            lines.append("\nmaxsavefilenum=" + str(obj["savenum"]))
            lines.append("\n\n# チャンネル")
            lines.append("\nchannel=" + obj["channel"])
            lines.append("\n\n# 録音時間(分)")
            lines.append("\nrectime=" + str(obj["rectime"]))
            lines.append("\n\n# ファイル名（yyyymmdd_[X]の「X」の部分を指定）")
            lines.append("\nfilename=" + obj["name"])
            with open(str(Path(self.setting_dir) / obj["settingfile"]), 'w', encoding="utf-8") as f:
                f.writelines(lines)

    # スケジュールを読み込む
    def __schedule2object(self):
        p = Path(self.schedule_file)
        with open(str(p), "r", encoding="utf-8") as f:
            lines = f.readlines()
        slines = []
        for line in lines:
            if line.startswith("#") == False and "rec_set.sh" in line:
                slines.append(line.replace("\n", ""))
        rets = {}
        for sline in slines:
            tmp = sline.split(" ")
            rets[tmp.pop()] = tmp
        return rets

    # スケジュールを書き込む
    def __object2schedule(self):
        p = Path(self.schedule_file)
        with open(str(p), "r", encoding="utf-8") as f:
            lines = f.readlines()
        existkeys = []
        for i in range(len(lines)):
            for key in self.schedule.keys():
                if key in lines[i]:
                    l = self.schedule[key][0] + " " + self.schedule[key][1] + " " + self.schedule[key][2] + " " + self.schedule[key][3] + " " + self.schedule[key][4] + " " + self.schedule[key][5] + " " + self.schedule[key][6] + " " + key + "\n"
                    lines[i] = l
                    existkeys.append(key)
        createkeys = set(self.schedule.keys()) - set(existkeys)
        for key in createkeys:
            l = self.schedule[key][0] + " " + self.schedule[key][1] + " " + self.schedule[key][2] + " " + self.schedule[key][3] + " " + self.schedule[key][4] + " " + self.schedule[key][5] + " " + self.schedule[key][6] + " " + key + "\n"
            lines.append(l)
        with open(str(p), 'w', encoding="utf-8") as f:
            f.writelines(lines)

    # 録音設定追加
    def create(self, rs:RecSetting):
        prmnum = len(self.schedule) + 1
        # 設定ファイル作成
        ns = {}
        ns["savenum"] = rs.savenum
        ns["channel"] = rs.channel
        ns["rectime"] = rs.rectime
        ns["name"] = rs.name
        ns["settingfile"] = "rec_set" + str(prmnum) + ".prm"
        self.rec_set.append(ns)
        self.__object2setting()
        # スケジュール追加
        recset = self.setting_dir + "rec_set" + str(prmnum) + ".prm"
        for key in self.schedule.keys():
            if recset in key:
                self.schedule[key] = rs.schedule
                break
        if recset not in self.schedule.keys():
            self.schedule[recset] = rs.schedule
        self.__object2schedule()
        # ディレクトリ作成
        os.makedirs(self.save_dir + rs.name, exist_ok=True)
        return

    # 録音設定編集
    def edit(self, rs:RecSetting):
        # 元フォルダを取得
        for obj in self.rec_set:
            if obj["settingfile"] == rs.settingfile:
                name = obj["name"]
        # 設定ファイル、スケジュール削除
        self.delete(rs.settingfile, dirdel=False)
        # 設定ファイル、スケジュール追加
        self.create(rs)
        # 元フォルダと新フォルダが違う場合
        if rs.name != name:
            # 元フォルダの音源を新フォルダに移動する
            for f in glob.glob(self.save_dir + name + "/*"):
                shutil.copy(f, str(Path(self.save_dir) / rs.name))
            # 元フォルダを削除する
            shutil.rmtree(str(Path(self.save_dir) / name))
        return

    # 録音設定削除
    def delete(self, settingfile, dirdel=True):
        # 設定ファイル削除
        for i in range(len(self.rec_set)):
            if self.rec_set[i]["settingfile"] == settingfile:
                dirname = self.rec_set[i]["name"]
                self.rec_set.pop(i)
                break
        os.remove(str(Path(self.setting_dir) / settingfile))
        # スケジュール削除
        p = Path(self.schedule_file)
        with open(str(p), "r", encoding="utf-8") as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if settingfile in lines[i]:
                lines.pop(i)
        with open(str(p), 'w', encoding="utf-8") as f:
            f.writelines(lines)
        self.schedule = self.__schedule2object()
        # ディレクトリ削除
        if dirdel:
            shutil.rmtree(str(Path(self.save_dir) / dirname))
        return

    # 録音設定リストを出力
    def list(self):
        ret = []
        for set in self.rec_set:
            for key in self.schedule.keys():
                if set["settingfile"] in key:
                    k = key
                    break
            rs = RecSetting(set["channel"], set["rectime"], set["name"], self.schedule[k][4], self.schedule[k][1], self.schedule[k][0], set["savenum"], set["settingfile"])
            ret.append(rs.getObject())
        return ret

if __name__ == '__main__':
    setting_dir = "C:/Users/TAKUYA/Documents/vscode/RadikoPlayer/src/Recorder"
    schedule_file = "C:/Users/TAKUYA/Documents/vscode/RadikoPlayer/src/Recorder/radiko_schedule"
    RecorderSetting(setting_dir, schedule_file)
