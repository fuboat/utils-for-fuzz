#!/bin/bash

echo "exp_name;*;run time;map density;total execs;total paths;new edges on;now processing;cycles done;total crashes"

bash_command=$(cat /root/show-tmux-status.sh)
for container_name in $(docker inspect --format='{{.Name}}' $(docker ps -q) | cut -d"/" -f2 | sort)
do
    query=$(docker exec -it $container_name bash -c "$bash_command" | grep '%' | sed "s/^[^:]*:[^:]*://g")
    if [[ -z $query ]]
    then
	continue;
    else
	echo "$container_name: $query"
    fi
done
