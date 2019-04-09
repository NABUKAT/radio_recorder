#!/bin/bash

progname="RadikoPlayer"
lockfile="/var/lock/subsys/radikoplayer"
proc="python3"
rundir="/home/pi/RadikoPlayer/"
op="bottlerun.py"

case "$1" in
start)
    echo -n $"Starting $progname: "
    cd $rundir
    nohup $proc $op > /dev/null &
    pid=$!
    if [ "$?" -eq 0 ]; then
        echo -n $pid > $lockfile
    fi
;;
stop)
    echo -n $"Stopping $progname: "
    pid=`cat $lockfile`
    rm -f $lockfile
    kill -s 9 $pid
;;
*)
    echo $"Usage: $0 {start|stop}"
    exit 1
esac

exit $RETVAL