#!/bin/bash

echo "$(docker node ls)"
read -r id
docker node update "$id" --availability drain
sleep 1

while :
        do
                running=$(docker node ps "$id" | grep "Running" | xargs)
                if [[ -n "$running" ]]; then
                echo "$running"
                sleep 1
                else
                break
                fi
        done

echo "ready to reboot"
read
docker node update "$id" --availability active
