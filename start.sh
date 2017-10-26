#!/bin/bash
BIN_PATH=`dirname $0`
cd ${BIN_PATH}
pid=`ps -ef | grep scheduler | grep -v grep | grep cli.py | grep python | awk '{print $2}'`
if [ -z ${pid}  ]; then
    python cli.py scheduler
    echo "启动调度程序完成..."
else
    echo "调度程序已经启动..."
fi
