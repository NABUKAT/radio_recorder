#!/bin/bash

pid=$$
radikopy="/home/pi/radikopy/radiko.py"

# Usage
show_usage() {
  echo 'Usage:'
  echo ' RECORD MODE' 1>&2
  echo "   `basename $0` [-d out_dir] [-f file_name]" 1>&2
  echo '          [-t rec_minute] [-s Starting_position] channel' 1>&2
  echo '           -d  Default out_dir = $HOME' 1>&2
  echo '                  a/b/c = $HOME/a/b/c' 1>&2
  echo '                 /a/b/c = /a/b/c' 1>&2
  echo '                ./a/b/c = $PWD/a/b/c' 1>&2
  echo '           -f  Default file_name = channel_YYYYMMDD_HHMM_PID' 1>&2
  echo '           -t  Default rec_minute = 1' 1>&2
  echo '               60 = 1 hour, 0 = go on recording until stopped(control-C)' 1>&2
  echo '           -s  Default starting_position = 00:00:00' 1>&2
  echo ' PLAY MODE' 1>&2
  echo "   `basename $0` -p [-t play_minute] channel" 1>&2
  echo '           -p  Plya mode. No recording.' 1>&2
  echo '           -t  Default play_minute = 0' 1>&2
  echo '               60 = 1 hour, 0 = go on recording until stopped(control-C)' 1>&2
}

# Get Option
while getopts pd:f:t:s: OPTION
do
  case $OPTION in
    p ) OPTION_p=true
      ;;
    d ) OPTION_d=true
      VALUE_d="$OPTARG"
      ;;
    f ) OPTION_f=ture
      VALUE_f="$OPTARG"
      ;;
    t ) OPTION_t=true
      VALUE_t="$OPTARG"
      if ! expr "${VALUE_t}" : '[0-9]*' > /dev/null ; then
        show_usage ; exit 1
      fi
      ;;
    s ) OPTION_s=ture
      VALUE_s="$OPTARG"
      ;;
    * ) show_usage ; exit 1 ;;
  esac
done

# Get Channel
shift $(($OPTIND - 1))
if [ $# -ne 1 ]; then
  show_usage ; exit 1
fi
channel=$1

#
# RECORD Mode
#
if [ ! "${OPTION_p}" ]; then
  # Get Directory
  if [ ! "$OPTION_d" ]; then
    cd ${HOME}
  else
    if echo ${VALUE_d}|grep -q -v -e '^./\|^/'; then
      mkdir -p "${HOME}/${VALUE_d}"
      if [ $? -ne 0 ]; then
        echo "[stop] failed make directory (${HOME}/${VALUE_d})" 1>&2 ; exit 1
      fi
      cd "${HOME}/${VALUE_d}"
    else
      mkdir -p ${VALUE_d}
      if [ $? -ne 0 ]; then
        echo "[stop] failed make directory (${VALUE_d})" 1>&2 ; exit 1
      fi
      cd ${VALUE_d}
    fi
  fi
  outdir=${PWD}

  # Get File Name
  filename=${VALUE_f:=${channel}_${date}_${pid}}

  # Get Minute
  min=${VALUE_t:=1}

  #	debug
  # authorize && record
  python3 ${radikopy} record ${channel} ${min} ${outdir}/${filename}.aac

  #
  # PLAY Mode
  #
else
  #	debug
  python3 ${radikopy} play ${channel}

fi
