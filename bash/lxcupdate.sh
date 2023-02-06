#!/bin/bash

running=$(lxc list | grep "RUNNING" | grep "CONTAINER" | cut -d "|" -f2 | tr -d " ")

for container in $running
do
        lxc exec "$container" -- apt update
        lxc exec "$container" -- apt upgrade -y
        lxc exec "$container" -- apt autoremove -y
done
