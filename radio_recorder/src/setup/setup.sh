#!/bin/bash

if [ ! -e /usr/share/alsa/alsa.conf.bak ]; then
cp -np /usr/share/alsa/alsa.conf /usr/share/alsa/alsa.conf.bak
sed -i -e "s/defaults.ctl.card 0/defaults.ctl.card 1/g" /usr/share/alsa/alsa.conf
sed -i -e "s/defaults.pcm.card 0/defaults.pcm.card 1/g" /usr/share/alsa/alsa.conf
fi
if [ ! -e /etc/rc.local.bak ]; then
cp -np /etc/rc.local /etc/rc.local.bak
sed -i -e "s/exit 0//g" /etc/rc.local
echo "if [ -d /etc/rc.local.d ]; then">> /etc/rc.local
echo "  for i in /etc/rc.local.d/*; do">> /etc/rc.local
echo "    if [ -r \$i ]; then">> /etc/rc.local
echo "      . \$i">> /etc/rc.local
echo "    fi">> /etc/rc.local
echo "  done">> /etc/rc.local
echo "  unset i">> /etc/rc.local
echo "fi">> /etc/rc.local
echo "exit 0">> /etc/rc.local
fi
apt-get update
apt-get -y upgrade
apt-get -y install mplayer rtmpdump swftools libxml2-utils omxplayer
cd /tmp
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py
python3 get-pip.py
cd
pip3 install bottle
mkdir -p /media/radiko
mkdir -p /home/pi/RadikoRecorder/setting
exit 0
