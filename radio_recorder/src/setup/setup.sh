#!/bin/bash

if [ ! -e /usr/share/alsa/alsa.conf.bak ]; then
sudo cp -np /usr/share/alsa/alsa.conf /usr/share/alsa/alsa.conf.bak
fi
sudo sh -c "sed -i -e 's/defaults.ctl.card 0/defaults.ctl.card 1/g' /usr/share/alsa/alsa.conf"
sudo sh -c "sed -i -e 's/defaults.pcm.card 0/defaults.pcm.card 1/g' /usr/share/alsa/alsa.conf"
if [ ! -e /etc/rc.local.bak ]; then
sudo cp -np /etc/rc.local /etc/rc.local.bak
sed -i -e "s/exit 0//g" /etc/rc.local
sudo echo "if [ -d /etc/rc.local.d ]; then">> /etc/rc.local
sudo echo "  for i in /etc/rc.local.d/*; do">> /etc/rc.local
sudo echo "    if [ -r \$i ]; then">> /etc/rc.local
sudo echo "      . \$i">> /etc/rc.local
sudo echo "    fi">> /etc/rc.local
sudo echo "  done">> /etc/rc.local
sudo echo "  unset i">> /etc/rc.local
sudo echo "fi">> /etc/rc.local
sudo echo "exit 0">> /etc/rc.local
fi
sudo apt-get update
sudo apt-get -y upgrade
sudo apt --fix-broken -y install
sudo apt-get -y install mplayer rtmpdump swftools libxml2-utils omxplayer
cd /tmp
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
sudo python3 get-pip.py
cd
sudo pip3 install bottle
sudo mkdir -p /media/radiko
sudo mkdir -p /home/pi/RadikoRecorder/setting
exit 0
