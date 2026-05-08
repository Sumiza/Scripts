#!/bin/bash
#-------- Settings -----------
checktime=240   #-- Check the last minutes of log for failed login attempts - 60 = 1 hour / 720 = 12 hours / 1440 = 24 hours
tries=4         #-- Allowed login tries (+one try counts as a disconnect from server) in checktime
bantime=0       #-- Time for IP to stay banned in minutes  - 0 to never remove
#-----------------------------
curtime=$(date +%s)
ipall=$(/sbin/iptables -L INPUT -v -n  | grep "Bantime:" | tr -s " ")
try=$(journalctl -u ssh --since "$checktime minutes ago" | grep 'Failed password for\|Disconnected from invalid user\|Disconnected from authenticating user\|Connection closed by invalid user\|Connection closed by authenticating user' | rev |cut -d ' ' -f4 | rev | sort)
for i in $(uniq <<< "$try")
do
        if [ "$(grep -c <<< "$try" "$i")" -gt $tries ]; then
                if [ "$( grep -c <<< "$ipall" "$i")" -eq 0 ]; then
                       /sbin/iptables -A INPUT -s "$i" -j DROP -m comment --comment "Bantime: $(date +%s) - $(date)"
                fi
        fi
done
if [ $bantime != 0 ]; then
        bansec=$((bantime*60))
        while read -r line
        do
                if [ "$curtime" -gt $(("$(echo "$line" | cut -d ' ' -f12)"+bansec)) ]; then
                        /sbin/iptables -D INPUT -s "$(echo "$line" | cut -d ' ' -f8)" -j DROP -m comment --comment "$(echo "$line" | cut -d '*' -f4 | awk '{$1=$1};1')"
                fi
        done <<< "$ipall"
fi
