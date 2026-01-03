#!/bin/bash

selfnode=$(docker node ls | grep "*"| cut -d " " -f 1)

docker node update "$selfnode" --availability drain
while :
        do
                running=$(docker node ps "$selfnode" | grep "Running")
                if [[ -n "$running" ]]; then
                        echo "$running"
                        sleep 1
                else
                        break
                fi
        done
apt update
apt upgrade -y
apt autoremove -y
docker node update "$selfnode" --availability active
reboot now
