#!/usr/bin/env bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
if [[ -f ./scheduler.pid ]]; then
    PID=`cat ./scheduler.pid`
    if ps -p $PID > /dev/null; then
        echo $PID
    fi
fi
