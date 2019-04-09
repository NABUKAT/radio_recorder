# -*- coding: utf-8 -*-

import paramiko
import scp
import json
import os
import re
from datetime import datetime

#------------------------------
# 設定ファイル読み込み
#------------------------------
setting_file = os.path.join(os.path.dirname(__file__), '../setting.json')
f = open(setting_file, 'r', encoding="utf-8")
setting = json.load(f)
f.close()
ip_file = os.path.join(os.path.dirname(__file__), '../ip.txt')
f = open(ip_file, 'r')
ip = f.read()
f.close()

#------------------------------
# 更新日時を更新
#------------------------------
now_unix = datetime.now().timestamp()
f = open("update_time.txt", "w")
f.write(str(int(now_unix)))
f.close()

#------------------------------
# デプロイ処理
#------------------------------
print("デプロイ処理を実行しています…")
with paramiko.SSHClient() as ssh:
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=setting["account"]["user"], password=setting["account"]["pass"])
    for f in setting["deploy_files"]:
        with scp.SCPClient(ssh.get_transport()) as lscp:
            try:
                # /tmpにSCP
                lscp.put(f["local_filepath"], "/tmp")
                # リモートパスをmkdir -p
                stdin, stdout, stderr = ssh.exec_command("echo " + setting["account"]["pass"] + " | sudo -S mkdir -p " + f["remote_directory"])
                for i in stdout:
                    print(i)
                # mvで/tmpのファイルをリモートパスに移動
                filename = re.sub(r".*/", "", f["local_filepath"])
                stdin, stdout, stderr = ssh.exec_command("echo " + setting["account"]["pass"] + " | sudo -S mv -f /tmp/" + filename + " " + f["remote_directory"])
                for i in stdout:
                    print(i)
                # chown、chmodを実行
                stdin, stdout, stderr = ssh.exec_command("echo " + setting["account"]["pass"] + " | sudo -S chown " + f["user"] + ":" + f["group"] + " " + (f["remote_directory"] + "/" + filename).replace("//", "/"))
                for i in stdout:
                    print(i)
                stdin, stdout, stderr = ssh.exec_command("echo " + setting["account"]["pass"] + " | sudo -S chmod " + f["permission"] + " " + (f["remote_directory"] + "/" + filename).replace("//", "/"))
                for i in stdout:
                    print(i)
                print((f["remote_directory"] + "/" + filename).replace("//", "/") + "を配置しました")
            except FileNotFoundError:
                print(f["local_filepath"] + "は存在しません。スキップします。")

#------------------------------
# 現行プロセスを止める
#------------------------------
    if setting["process_dn_com"] != "none":
        print("現行プロセスを停止します。")
        stdin, stdout, stderr = ssh.exec_command("echo " + setting["account"]["pass"] + ' | sudo -S sh -c "' + setting["process_dn_com"] + '"')
        for i in stdout:
            print(i)
            break

#------------------------------
# 新規プロセスを立ち上げる
#------------------------------
    if setting["process_up_com"] != "none":
        print("新規プロセスを立ち上げます。")
        stdin, stdout, stderr = ssh.exec_command("echo " + setting["account"]["pass"] + ' | sudo -S sh -c "' + setting["process_up_com"] + '"')
        for i in stdout:
            print(i)
            break
