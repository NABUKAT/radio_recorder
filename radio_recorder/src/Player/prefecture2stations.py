# -*- coding: utf-8 -*-

import json
import os.path

def Prefecture2Stations(prefecture):
    try:
        currentpath = os.path.dirname(os.path.abspath(__file__))
        # 局リストを読み込む
        f = open(os.path.join(currentpath, "stationlist.json"), "r", encoding="utf-8_sig")
        stationlist = f.read()
        f.close()
        sljson = json.loads(stationlist)

        # 地域⇒局リスト
        ret = sljson[prefecture]

        return json.dumps(ret, ensure_ascii=False)
    except KeyError:
        return ""

if __name__ == '__main__':
    p2s = Prefecture2Stations("青森県")
    print(p2s)