# -*- coding: utf-8 -*-

import os
import json

from listenmanagement import ListenManagement

def dirToList(dir):
    rets = {}
    rets[dir] = sorted(os.listdir(dir))
    for i in range(len(rets[dir])):
        # ディレクトリの場合
        if os.path.isfile(dir + "/" + rets[dir][i]) == False:
            rets[dir][i] = dirToList(dir + "/" + rets[dir][i])
    return rets

def dirToListJson(dir):
    ret = {}
    lm = ListenManagement()
    ret["lm"] = lm.get()
    ret["dir"] = dirToList(dir)
    return json.dumps(ret, ensure_ascii=False)
    
if __name__ == '__main__':
    print(dirToListJson("/media/radiko"))
