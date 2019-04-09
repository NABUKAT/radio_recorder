#!/bin/bash

#--------------------#
#   パラメータ設定   #
#--------------------#

. $1

#--------------------#
# 古いファイルの削除 #
#--------------------#

cd $savefolder
filecount=`ls | wc -l`
if [ $filecount -ge $maxsavefilenum ] ; then
  echo ファイルを削除します
  ls -tr | head -1 | xargs rm
fi

#--------------------#
#      録音実行      #
#--------------------#

dateym=`date +%Y%m%d`
/home/pi/RadikoRecorder/bin/radiko.sh -d $savefolder -f ${dateym}_$filename -t $rectime $channel