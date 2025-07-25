#!/bin/sh

FILENAME="$1"  # First argument: Docker Compose file
name=$(echo "$FILENAME" | cut -d '.' -f 1)  # Extract stack base name from file
DOCKER=$(command -v docker)  # Find docker binary location

# Get list of all Docker nodes with their status and availability
get_nodes(){
    "$DOCKER" node ls --format "{{.Hostname}} {{.Status}} {{.Availability}}"
}

# Get list of currently running stack names
get_stack(){
    "$DOCKER" stack ls --format "{{.Name}}"
}

# Remove all stacks matching the naming pattern across all nodes
remove_all_stacks(){
    nodes=$(get_nodes | cut -d ' ' -f 1)
    for node in $nodes; do
        remove_one "$node"
    done 
}

# Re-deploy stacks that already exist on active nodes
update_stack(){
    stacks=$(get_stack)
    nodes=$(get_nodes | cut -d ' ' -f 1)
    for node in $nodes; do
        if echo "$stacks" | grep -q "$name-$node"; then
            if [ "$1" = "--force" ]; then
                for service in $("$DOCKER" stack services -q "$name-$node"); do
                    "$DOCKER" service update -d "$service" --force
                done
            else
                deploy_one "$node"
            fi
        fi
    done
}

# Remove stacks on nodes that are not Ready and Active
clean_inactive_nodes(){
    nodes=$(get_nodes | grep -v "Ready Active" | cut -d ' ' -f 1)
    stacks=$(get_stack)
    for node in $nodes; do
        if echo "$stacks" | grep -q "$name-$node"; then
            remove_one "$node"
        fi
    done
}

remove_one(){
    "$DOCKER" stack rm "$name"-"$1" 2> /dev/null
    sleep 5 # allows Docker to clean up networks properly before next operation
}

# Deploy stack to a specific node with a constraint
deploy_one(){
    if grep -q "node.hostname == ${TARGET_NODE}" "$FILENAME"; then
        sed "s|\${TARGET_NODE}|$1|g" "$FILENAME" > docker_pod_temp_$$.yml
        "$DOCKER" stack deploy -d -c "docker_pod_temp_$$.yml" "$name"-"$1"
        [ -f docker_pod_temp_$$.yml ] && rm docker_pod_temp_$$.yml
    else
        "$DOCKER" stack deploy -d -c "$FILENAME" "$name"-"$1"
    fi
    # same constraint can be added twice
    for serviceID in $("$DOCKER" stack services "$name"-"$1" -q); do
        "$DOCKER" service update -d --constraint-add "node.hostname == $1" "$serviceID"
    done
    sleep 5 # without this sometimes commands would not propagate
}

# Deploy stack globally to all (or --all) nodes that don't already have it
deploy_global(){
    nodes=$(get_nodes | grep "Ready Active" | cut -d ' ' -f 1)
    stacks=$(get_stack)
    if [ "$1" = "--all" ]; then
        nodes=$(get_nodes | cut -d ' ' -f 1)
    fi
    for node in $nodes; do
        if ! echo "$stacks" | grep -q "$name-$node"; then
            deploy_one "$node"
        fi
    done
}

# Deploy to a specific number of nodes
deploy_n_replicas(){
    replicate=$1
    stacks=$(get_stack)
    nodes=$(get_nodes | cut -d ' ' -f 1)
    usednodes=""

    # Identify nodes already running the stack
    for node in $nodes; do
        if echo "$stacks" | grep -q "$name-$node"; then
            usednodes="$node $usednodes"
            replicate=$((replicate - 1))
        fi
    done

    [ "$replicate" -eq 0 ] && return

    # If too many replicas exist, randomly remove extras
    if [ "$replicate" -lt 0 ]; then
        for node in $(echo "$usednodes" | tr ' ' '\n' | shuf); do
            remove_one "$node"
            replicate=$((replicate + 1))
            [ "$replicate" -eq 0 ] && return
        done
    fi

    # Deploy to additional random Ready Active nodes as needed
    readynodes=$(get_nodes | grep "Ready Active" | cut -d ' ' -f 1 | shuf)
    if [ "$(echo "$readynodes" | wc -w)" -ge 1 ]; then
        for node in $readynodes; do
            if ! echo "$usednodes" | grep -q "$node"; then
                deploy_one "$node"
                replicate=$((replicate - 1))
            fi
            [ "$replicate" -eq 0 ] && return
        done
    fi
}

# Handle subcommands and help
if [ $# -lt 2 ] || [ "$2" = "help" ] || [ "$2" = "--help" ] || [ "$2" = "-h" ]; then
    echo
    echo "Docker Stack Orchestration Script"
    echo
    echo "Usage:"
    echo "  ./run <compose-file.yml> <command> [options]"
    echo
    echo "Commands:"
    echo "  deploy [N]        Deploy the stack to N active nodes"
    echo "  deploy --all      Deploy the stack to all nodes (ready or not)"
    echo "  update            Update stacks that already exist"
    echo "  remove            Remove all deployed stacks"
    echo "  clean             Remove stacks from inactive or unreachable nodes"
    echo "  help              Show this help message"
    echo
    echo "Arguments:"
    echo "  <compose-file.yml>  Path to a Docker Compose file"
    echo
    echo "Behavior:"
    echo "  - Each stack is deployed to a single, randomly selected node."
    echo "  - All services within the stack are restricted to run only on that node."
    echo "  - This ensures the stack is not spread across multiple nodes."
    echo "  - Mimics Kubernetes pod-level scheduling on a per-node basis."
    echo "  - Useful for isolating workloads per node."
    echo "  - Stack names follow the pattern: <basename>-<node>"
    echo
    echo "Maintenance:"
    echo "  - If a node goes offline, the associated stack becomes unreachable."
    echo "  - Run './run <file> clean' to remove stacks from inactive nodes."
    echo "  - Then run './run <file> deploy <count>' to restore the desired number of stacks."
    echo "  - These steps can be automated via a cron job for self-healing."
    echo "  - Example (every 5 minutes to maintain 3 running stacks):"
    echo "    */5 * * * * /path/to/run my-compose.yml clean && /path/to/run my-compose.yml deploy 3"
    echo
    echo "(OPTIONAL) Compose File Notes:"
    echo "  - Use '\${TARGET_NODE}' in your Compose file's placement constraints."
    echo "  - The script replaces \${TARGET_NODE} with the appropriate hostname during deployment."
    echo "  - Example constraint: node.hostname == \${TARGET_NODE}"
    echo "  - This is optional but ensures containers are not placed on unintended nodes before assignment."
    echo
    echo "Examples:"
    echo "  ./run app.yml deploy           Deploy to all available nodes"
    echo "  ./run app.yml deploy 3         Deploy to 3 available nodes"
    echo "  ./run app.yml deploy --all     Deploy to all known nodes (including offline / drain nodes)"
    echo "  ./run app.yml update           Update only existing stacks"
    echo "  ./run app.yml clean            Remove stacks from inactive nodes"
    echo "  ./run app.yml remove           Remove all deployed stacks"
    echo
    echo "Notes:"
    echo "  - Compose files may use \${TARGET_NODE} for node affinity."
    echo "  - Requires Docker Swarm (uses 'docker stack' and 'docker node' commands)."
    echo

elif [ "$2" = "remove" ]; then
    remove_all_stacks

elif [ "$2" = "clean" ]; then
    clean_inactive_nodes

elif [ "$2" = "update" ]; then
    if [ "$3" = "--force" ]; then
        update_stack "$3"
    else
        update_stack
    fi

elif [ "$2" = "deploy" ]; then
    if [ "$3" = "--all" ]; then
        deploy_global "$3"
    elif [ "$3" ]; then
        deploy_n_replicas "$3"
    else
        deploy_global
    fi
fi
