#!/bin/bash
hours=1
tries=5
bantime=24
for i in $(journalctl -u ssh --since "$hours hour ago" | grep
'Disconnected from invalid user\|Disconnected from authenticating
user\|Connection closed by invalid user\|Connection closed by
authenticating user' | rev |cut -d ' ' -f4 | rev | sort | uniq)
do
         if [ "$(grep -c "$i" /etc/hosts.deny)" -eq 0 ]; then
                 if [ "$(grep -c "$i" /var/log/auth.log)" -gt $tries ]; then
                        echo "ALL : $i" >> /etc/hosts.deny
                 fi
         fi
done

for i in $(cat /etc/hosts.deny | grep "^ALL : " | cut -d ' ' -f3)
do
         if [ "$(journalctl -u ssh --since "$bantime hour ago" | grep -c"$i")" -eq 0 ]; then
                 sed -i "$(grep -n "$i" /etc/hosts.deny | cut -d ':' -f1)d" /etc/hosts.deny
         fi
done
