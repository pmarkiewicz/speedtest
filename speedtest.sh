#!/bin/bash
#
# speedtest      Startup script for speedtest
#
# chkconfig: - 87 12
# description: speedtest is internet speed measure daemon
# config: /etc/speedtest/speedtest.conf
# config: /etc/sysconfig/speedtest
# pidfile: /var/run/speedtest.pid
#
### BEGIN INIT INFO
# Provides: speedtest
# Required-Start: $local_fs
# Required-Stop: $local_fs
# Short-Description: start and stop speedtest server
# Description: speedtest is a dummy Python-based daemon
### END INIT INFO

# Source function library.
. /etc/rc.d/init.d/functions

if [ -f /etc/sysconfig/speedtest ]; then
        . /etc/sysconfig/speedtest
fi

speedtest=/var/lib/speedtest/speedtest.py
prog=speedtest
pidfile=${PIDFILE-/var/run/speedtest.pid}
logfile=${LOGFILE-/var/log/speedtest.log}
RETVAL=0

OPTIONS=""

start() {
        echo -n $"Starting $prog: "

        if [[ -f ${pidfile} ]] ; then
            pid=$( cat $pidfile  )
            isrunning=$( ps -elf | grep  $pid | grep $prog | grep -v grep )

            if [[ -n ${isrunning} ]] ; then
                echo $"$prog already running"
                return 0
            fi
        fi
        $speedtest -p $pidfile -l $logfile $OPTIONS
        RETVAL=$?
        [ $RETVAL = 0 ] && success || failure
        echo
        return $RETVAL
}

stop() {
    if [[ -f ${pidfile} ]] ; then
        pid=$( cat $pidfile )
        isrunning=$( ps -elf | grep $pid | grep $prog | grep -v grep | awk '{print $4}' )

        if [[ ${isrunning} -eq ${pid} ]] ; then
            echo -n $"Stopping $prog: "
            kill $pid
        else
            echo -n $"Stopping $prog: "
            success
        fi
        RETVAL=$?
    fi
    echo
    return $RETVAL
}

reload() {
    echo -n $"Reloading $prog: "
    echo
}

# See how we were called.
case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  status)
    status -p $pidfile $speedtest
    RETVAL=$?
    ;;
  restart)
    stop
    start
    ;;
  force-reload|reload)
    reload
    ;;
  *)
    echo $"Usage: $prog {start|stop|restart|force-reload|reload|status}"
    RETVAL=2
esac

exit $RETVAL
