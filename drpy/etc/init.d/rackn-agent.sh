#!/bin/sh
#
# Start / Stop drpy
#
# chkconfig: 345 90 10
#
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

name=`basename $0`
dir="/opt/rackn/drpy"
pid_file="$dir/$name.pid"
DS_PATH=$(localcli --formatter json storage filesystem list|python -c "import sys,json;x=json.load(sys.stdin);y=[i for i in x if i['Type']=='VFFS' or 'vmfs' in i['Type'].lower()];print(y[0]['Mount Point'])")
cmd="python agent -f ${DS_PATH}/rackn/drpy.conf"


get_pid() {
    cat "$pid_file"
}

is_running() {
    [ -f "$pid_file" ] && ps -cgi|grep `get_pid`|grep -v grep > /dev/null 2>&1
}

case "$1" in
    start)
        if is_running; then
            echo "drpy is already running"
            exit
        fi
        echo "Starting $name"
        cd "$dir"
        if [ -f "${DS_PATH}/rackn/drpy.conf" ]; then
            $cmd &
            echo $! > "$pid_file"
            if ! is_running; then
                echo "Unable to start"
                exit 1
            fi
        fi
        echo "Config file not found During startup." >> drpy.log
        exit 1
    ;;
    stop)
        echo "Use kill `get_pid` instead."
    ;;
    *)
    echo "Usage: $0 {start|stop}"
    exit 1
    ;;
esac

exit 0
