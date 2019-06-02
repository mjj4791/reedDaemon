#!/bin/bash

TAG=reedDameon
REED_DIR=/home/pi/reed
REEDDAEMON=reedDaemon

watch() {
    count=0
    while true; do
        sleep 5
        if ! ps aux | grep ${REEDDAEMON}.py | grep -v grep &>/dev/null; then
            /usr/bin/logger -t $TAG -s "not running, respawning"
            start
        fi
    done
}

function status() {
    echo "Checking status...."
    pid=$(ps -ef | grep ${REEDDAEMON}.py | grep -v grep | tr -s ' ' | sed -e 's/^\s//' | cut -d ' ' -f 2)
    if [ -n "$pid" ]; then
        echo "$TAG is running with pid $pid"
    else
		echo "$TAG is NOT running"
    fi
}

function start() {
	echo "Starting ${REEDDAEMON}..."
    pid=$(ps -ef | grep ${REEDDAEMON}.py | grep -v grep | tr -s ' ' | sed -e 's/^\s//' | cut -d ' ' -f 2)
    if [ -n "$pid" ]; then
		echo "${TAG} already running with pid $pid."
        
        pid=$(ps -ef | grep ${REEDDAEMON}.sh | grep -v grep | grep -v $$ | grep -v sudo | tr -s ' ' | sed -e 's/^\s//' | cut -d ' ' -f 2)
        if [ ! -z "$pid" ]; then
            # another watchdog is running, so exit
            exit
        fi
        # we will become the watchdog, by returning:
        return
    fi
    # not running, so start and return:
    cd $REED_DIR
    ./${REEDDAEMON}.py > /dev/null 2>&1 &
}

function stop() {
	# stop the watch/daemon script
	# echo $$
	pid=$(ps -ef | grep ${REEDDAEMON}.sh | grep -v grep | grep -v $$ | grep -v sudo | tr -s ' ' | sed -e 's/^\s//' | cut -d ' ' -f 2)
    if [ ! -z "$pid" ]; then
		# forcefully kill the watchdog
		echo "Stopping $TAG watchdog ($pid)..."
		echo $pid | xargs kill -KILL  &>/dev/null
    fi

	# stop the process
	pid=$(ps -ef | grep ${REEDDAEMON}.py | grep -v grep | grep -v $$ | tr -s ' ' | sed -e 's/^\s//' | cut -d ' ' -f 2)
    if [ -z "$pid" ]; then
        return
    fi
    
    echo $pid | xargs kill -HUP  &>/dev/null
    count=0
    while echo $pid | xargs kill -0 &>/dev/null && [ $count -lt 5 ]; do
        echo -n  .
		sleep 1
        count=$(($count + 1))
    done
	echo "Stopping $TAG ($pid)..."
    echo $pid | xargs kill -KILL &>/dev/null
}

case "$1" in
    start)
        start
        watch &
        ;;

    stop)
        stop
        ;;
    status)
        status
        ;;
    restart)
        stop
        start
        watch &
        ;;

    *)
        echo $"Usage: $0 {start|stop|status|restart}"
        exit 1
	;;
esac

