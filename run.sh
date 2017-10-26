#!/bin/bash

#source `dirname $0`/env.sh

start() {
	sh start.sh
}

stop() {
	sh stop.sh
}

restart() {
	sh stop.sh
	sh start.sh
}


case "$1" in
	start|stop|restart)
  		$1
		;;
	*)
		echo $"Usage: $0 {start|stop|restart}"
		exit 1
esac