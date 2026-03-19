#!/bin/sh

DEPENDENCY_HOST="depend_on"

delay_shutdown() {

  while true
  do
    if ping -c 1 "$DEPENDENCY_HOST" >/dev/null 2>&1; then
        echo "$DEPENDENCY_HOST is up, waiting...."
        sleep 1
    else
        echo "$DEPENDENCY_HOST is down."
        kill -TERM "$MAIN_PID"
        break
    fi
done
}

trap delay_shutdown TERM

"$@" & MAIN_PID=$!
echo "$MAIN_PID"

wait "$MAIN_PID"
