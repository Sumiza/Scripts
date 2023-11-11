#!/bin/bash
echo "Commands:
        add - new port forward
        remove - remove a port forward
        list - show all the port forwards
        done - will save and exit"
while :
do
        read -r cmd
        
        if [ "$cmd" = "add" ]; then
                echo "(inbound port) (type tcp/udp) (destination ip) (destination port) (interface (optional))"
                read -r inport type destip destport interface
                
                if ! [ "$interface" = "" ]; then
                        interface="-i $interface "
                fi
                
                iptables -t nat -A PREROUTING "$interface" -p "$type" --dport "$inport" -j DNAT --to-destination "$destip":"$destport"
                
        elif [ "$cmd" = "remove" ]; then
                iptables -t nat -v -L -n --line-number | grep "DNAT"
                echo "what number rule would you like to delete"
                read -r delnr
                iptables -t nat -D PREROUTING "$delnr"
                
        elif [ "$cmd" = "done" ]; then
                /sbin/iptables-save > /etc/iptables/rules.v4
                break
        fi
        
        iptables -t nat -L -v | grep "DNAT"

done
