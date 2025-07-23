#!/bin/bash

if [ -z "$1" ]; then
    echo "Compose stack yml file needed (./run file.yml)"
    exit 1
fi

filename="$1"
name=$(echo "$filename" | cut -d '.' -f 1)

removeall(){
    nodes=$(/usr/bin/docker node ls --format "{{.Hostname}}")
    for node in ${nodes}; do
        docker stack rm "$filename" "$name"-"$node" 2> /dev/null
    done 
}

update(){
    stacks=$(/usr/bin/docker stack ls --format "{{.Name}}")
    nodes=$(/usr/bin/docker node ls --format "{{.Hostname}}")
    for node in ${nodes};do
        stackname="$name"-"$node"
        if echo "$stacks" | grep -q "$stackname"; then
            /usr/bin/docker stack deploy -d -c "$filename" "$name"-"$node" 
        fi
    done
}

cleanup(){
    nodes=$(/usr/bin/docker node ls --format "{{.Hostname}} {{.Status}} {{.Availability}}" | grep -v "Ready Active" | cut -d ' ' -f 1)
    for node in ${nodes}; do
        /usr/bin/docker stack rm "$name"-"$node" 2> /dev/null
    done
}

deployone(){
    /usr/bin/docker stack deploy -d -c "$filename" "$name"-"$1"
    serviceID=$(/usr/bin/docker stack services "$name"-"$1" -q)
    /usr/bin/docker service update -d --constraint-add node.hostname=="$1" "$serviceID"
}

deployglobal(){
    nodes=$(/usr/bin/docker node ls --format "{{.Hostname}} {{.Status}} {{.Availability}}" | grep "Ready Active" | sort | cut -d ' ' -f 1)
    for node in ${nodes};do
            deployone "$node"
    done
}

deployn(){
    replicate=$1
    stacks=$(/usr/bin/docker stack ls --format "{{.Name}}")
    nodes=$(/usr/bin/docker node ls --format "{{.Hostname}}")
    usednodes=()
    for node in ${nodes};do
        stackname="$name"-"$node"
        if echo "$stacks" | grep -q "$stackname"; then
            usednodes+=("$node")
            ((replicate--))
        fi
    done

    if [ "$replicate" -eq 0 ]; then
        exit 0
    fi

    if [ "$replicate" -lt 0 ]; then
        usednodesrandom=$(echo "${usednodes[@]}" | tr ' ' '\n' | sort -R)
        for node in ${usednodesrandom}; do
            /usr/bin/docker stack rm -d  "$name"-"$node"
            ((replicate++))
            if [ "$replicate" -eq 0 ]; then
                exit 0
            fi
        done
    fi

    readynodes=$(/usr/bin/docker node ls --format "{{.Hostname}} {{.Status}} {{.Availability}}" | grep "Ready Active" | sort -R | cut -d ' ' -f 1)
    readynodecount=$(echo "$readynodes" | wc -w)

    if [ "$readynodecount" -ge 1 ]; then
        for node in ${readynodes};do
            if echo "${usednodes[@]}" | grep -v -q "$node"; then
                deployone "$node"
                ((replicate--))
            fi
            if [ "$replicate" -eq 0 ]; then
                exit 0
            fi
        done
    fi
}

if [ "$2" == "remove" ]; then
    removeall

elif [ "$2" == "clean" ]; then
    cleanup

elif [ "$2" == "update" ]; then
    update

elif [ "$2" == "deploy" ]; then
    if [ "$3" ]; then
        deployn "$3"
    else
        deployglobal
    fi    
fi
