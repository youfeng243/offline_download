#!/bin/bash
BIN_PATH=`dirname $0`
cd ${BIN_PATH}
python cli.py scheduler stop
echo "退出调度程序完成..."