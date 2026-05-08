#!/bin/bash

#--login info 
whotemp=$(who | tr  -s ' ' | tr -d '()')

locinfo=$(curl -s ipinfo.io/"$(cut -d ' ' -f5 <<< "$whotemp")")

body="Login detected at $(date) for:
Hostname        : $(hostname)
IP(s)           : $(hostname -I)

User information:
User            : $(cut -d ' ' -f1 <<< "$whotemp")
User IP         : $(cut -d ' ' -f5 <<< "$whotemp")
User Hostname   : $(host "$(cut -d ' ' -f5 <<< "$whotemp")" | rev | cut -d ' ' -f1 | rev)
User Location   : $(grep <<< "$locinfo" '"city"' | cut -d '"' -f4), $(grep <<< "$locinfo" '"region"' | cut -d '"' -f4), $(grep <<< "$locinfo" '"country"' | cut -d '"' -f4)
User ISP        : $(grep <<< "$locinfo" '"org"' | cut -d '"' -f4)"
echo "$body"

discordtoken=""
curl -H "Content-Type: application/json" \
-d "{\"username\": \"$(hostname) login\", \"content\": \"$body\"}" \
https://discord.com/api/webhooks/123/"$discordtoken"
