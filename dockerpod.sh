#!/bin/sh

# Check for minimum 2 arguments: the compose file and a command
if [ $# -lt 2 ]; then
    echo "Usage: ./run <compose-file.yml> [remove|clean|update|deploy [replicas|--all]]"
    exit 1
fi

FILENAME="$1"  # First argument: Docker Compose file
name=$(echo "$FILENAME" | cut -d '.' -f 1)  # Extract stack base name from file
DOCKER=$(command -v docker)  # Find docker binary location

# Get list of all Docker nodes with their status and availability
get_nodes(){
    $DOCKER node ls --format "{{.Hostname}} {{.Status}} {{.Availability}}"
}

# Get list of currently running stack names
get_stack(){
    $DOCKER stack ls --format "{{.Name}}"
}

# Remove all stacks matching the naming pattern across all nodes
remove_all_stacks(){
    nodes=$(get_nodes | cut -d ' ' -f 1)
    for node in ${nodes}; do
        $DOCKER stack rm "$name"-"$node" 2> /dev/null
    done 
}

# Re-deploy stacks that already exist on active nodes
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

# Remove stacks on nodes that are not Ready and Active
clean_inactive_nodes(){
    nodes=$(get_nodes | grep -v "Ready Active" | cut -d ' ' -f 1)
    for node in ${nodes}; do
        $DOCKER stack rm "$name"-"$node" 2> /dev/null
    done
}

# Deploy stack to a specific node with a constraint
deploy_one(){
    $DOCKER stack deploy -d -c "$FILENAME" "$name"-"$1"
    serviceID=$($DOCKER stack services "$name"-"$1" -q)
    for serviceID in $($DOCKER stack services "$name"-"$1" -q); do
    $DOCKER service update -d --constraint-add node.hostname=="$1" "$serviceID"
done
}

# Deploy stack globally to all (or --all) nodes that don't already have it
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

# Exit early if the target number of replicas is already satisfied
check_done(){
    if [ "$1" -eq 0 ]; then
        exit 0
    fi
}

# Deploy to a specific number of nodes
deploy_n_replicas(){
    replicate=$1
    stacks=$(get_stack)
    nodes=$(get_nodes | cut -d ' ' -f 1)
    usednodes=""

    # Identify nodes already running the stack
    for node in $nodes; do
        stackname="$name"-"$node"
        if echo "$stacks" | grep -q "$stackname"; then
            usednodes="$node $usednodes"
            replicate=$((replicate - 1))
        fi
    done

    check_done "$replicate"

    # If too many replicas exist, randomly remove extras
    if [ "$replicate" -lt 0 ]; then
        usednodesrandom=$(echo "$usednodes" | tr ' ' '\n' | sort -R)
        for node in ${usednodesrandom}; do
            $DOCKER stack rm "$name"-"$node"
            replicate=$((replicate + 1))
            check_done $replicate
        done
    fi

    # Deploy to additional Ready Active nodes if needed
    readynodes=$(get_nodes | grep "Ready Active" | sort -R | cut -d ' ' -f 1)
    readynodecount=$(echo "$readynodes" | wc -w)

    if [ "$readynodecount" -ge 1 ]; then
        for node in ${readynodes}; do
            if ! echo "$usednodes" | grep -q "$node"; then
                deploy_one "$node"
                replicate=$((replicate - 1))
            fi
            check_done "$replicate"
        done
    fi
}

# Handle subcommands
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
