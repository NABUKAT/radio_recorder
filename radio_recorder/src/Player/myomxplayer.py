# -*- coding: utf-8 -*-
import os
import signal
import subprocess
import time

class MyOmxplayer:
    def newplay(self, filepath):
        self.stop()
        command = 'exec omxplayer -o alsa ' + filepath
        subprocess.Popen(command, shell=True, stdin=subprocess.PIPE)
        self.setState("play")

    def stop(self):
        if self.getState() == "play":
            self.pid = subprocess.Popen("ps aux | grep -v grep | grep ' -o alsa ' | awk '{print $2}'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
            self.pid = self.pid.splitlines()
            for p in self.pid:
                print(p)
                os.kill(int(p), signal.SIGTERM)
            self.setState("stop")

    def play(self):
        if self.getState() == "pause":
            self.command("p")
            self.setState("play")
        
    def pause(self):
        if self.getState() == "play":
            self.command("p")
            self.setState("pause")

    def p30(self):
        if self.getState() != "stop":
            self.command("^[[C")
            
    def p600(self):
        if self.getState() != "stop":
            self.command("^[[A")
        
    def m30(self):
        if self.getState() != "stop":
            self.command("^[[D")
        
    def m600(self):
        if self.getState() != "stop":
            self.command("^[[B")
            
    def confirm(self):
        self.pnum = subprocess.Popen("ps aux | grep -v grep | grep 'omxplayer -o alsa ' | wc -l", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        self.pnum = str(self.pnum, "utf-8").splitlines()
        if self.pnum[0] == "0":
            return "stop"
        return self.getState()
        
    def command(self, com):
        pid = subprocess.Popen("ps aux | grep -v grep | grep 'omxplayer -o alsa ' | awk '{print $2}'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        pid = str(pid, "utf-8").splitlines()
        for p in pid:
            print(os.path.join("/proc", p, "fd", "0"))
            with open(os.path.join("/proc", p, "fd", "0"), "w") as s:
                s.write(com)
            break

    def getState(self):
        f = open(os.path.join(os.path.dirname(__file__), "player_state.txt"), "r")
        state = f.read()
        f.close()
        return state

    def setState(self, state):
        f = open(os.path.join(os.path.dirname(__file__), "player_state.txt"), "w")
        f.write(state)
        f.close()
                                            
if __name__ == '__main__':
    filepath = "/media/radiko/伊集院光の深夜の馬鹿力/20181127_伊集院光の深夜の馬鹿力.m4a"
    mop = MyOmxplayer()
    mop.newplay(filepath)
    time.sleep(5)
    mop.p30()
    #mop.pause()
    #print(mop.confirm())
    #time.sleep(5)
    #mop.play()
    #time.sleep(5)
    #mop.stop()
