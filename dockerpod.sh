#!/bin/sh

if [ $# -lt 2 ]; then
    echo "Usage: ./run <compose-file.yml> [remove|clean|update|deploy [replicas|--all]]"
    exit 1
fi

FILENAME="$1"
name=$(echo "$FILENAME" | cut -d '.' -f 1)
DOCKER=$(command -v docker)

get_nodes(){
    $DOCKER node ls --format "{{.Hostname}} {{.Status}} {{.Availability}}"
}

get_stack(){
    $DOCKER stack ls --format "{{.Name}}"
}

remove_all_stacks(){
    nodes=$(get_nodes | cut -d ' ' -f 1)
    for node in ${nodes}; do
        $DOCKER stack rm "$name"-"$node" 2> /dev/null
    done 
}

update_stack(){
    stacks=$(get_stack)
    nodes=$(get_nodes | cut -d ' ' -f 1)
    for node in ${nodes}; do
        stackname="$name"-"$node"
        if echo "$stacks" | grep -q "$stackname"; then
            $DOCKER stack deploy -d -c "$FILENAME" "$name"-"$node" 
        fi
    done
}

clean_inactive_nodes(){
    nodes=$(get_nodes | grep -v "Ready Active" | cut -d ' ' -f 1)
    for node in ${nodes}; do
        $DOCKER stack rm "$name"-"$node" 2> /dev/null
    done
}

deploy_one(){
    $DOCKER stack deploy -d -c "$FILENAME" "$name"-"$1"
    serviceID=$($DOCKER stack services "$name"-"$1" -q)
    $DOCKER service update -d --constraint-add node.hostname=="$1" "$serviceID"
}

deploy_global(){
    nodes=$(get_nodes | grep "Ready Active" | sort | cut -d ' ' -f 1)
    stacks=$(get_stack)
    if [ "$1" = "--all" ]; then
        nodes=$(get_nodes | sort | cut -d ' ' -f 1)
    fi
    for node in ${nodes}; do
        stackname="$name"-"$node"
        if ! echo "$stacks" | grep -q "$stackname"; then
            deploy_one "$node"
        fi
    done
}
check_done(){
    if [ "$1" -eq 0 ]; then
        exit 0
    fi
}

deploy_n_replicas(){
    replicate=$1
    stacks=$(get_stack)
    nodes=$(get_nodes | cut -d ' ' -f 1)
    usednodes=""
    for node in $nodes;do
        stackname="$name"-"$node"
        if echo "$stacks" | grep -q "$stackname"; then
            usednodes="$node $usednodes"
            replicate=$((replicate - 1))
        fi
    done

    check_done "$replicate"

    if [ "$replicate" -lt 0 ]; then
        usednodesrandom=$(echo "$usednodes" | tr ' ' '\n' | sort -R)
        for node in ${usednodesrandom}; do
            $DOCKER stack rm "$name"-"$node"
            replicate=$((replicate + 1))
            check_done $replicate
        done
    fi

    readynodes=$(get_nodes | grep "Ready Active" | sort -R | cut -d ' ' -f 1)
    readynodecount=$(echo "$readynodes" | wc -w)

    if [ "$readynodecount" -ge 1 ]; then
        for node in ${readynodes};do
            if ! echo "$usednodes" | grep -q "$node"; then
                deploy_one "$node"
                replicate=$((replicate - 1))
            fi
            check_done "$replicate"
        done
    fi
}

if [ "$2" = "remove" ]; then
    remove_all_stacks

elif [ "$2" = "clean" ]; then
    clean_inactive_nodes

elif [ "$2" = "update" ]; then
    update_stack

elif [ "$2" = "deploy" ]; then

    if [ "$3" = "--all" ]; then
        deploy_global "$3"
    elif [ "$3" ]; then
        deploy_n_replicas "$3"
    else
        deploy_global
    fi

elif [ "$2" = "help" ]; then
    echo "Usage:"
    echo "  ./run file.yml deploy [count]  - Deploy to --all or N nodes"
    echo "  ./run file.yml update          - Update existing stacks"
    echo "  ./run file.yml remove          - Remove all stacks"
    echo "  ./run file.yml clean           - Remove stacks from inactive nodes"
    exit 0
fi
