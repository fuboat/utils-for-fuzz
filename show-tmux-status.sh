#!/bin/bash

show_content_by_tmux_session_and_windows_id() {
    # $1: session name
    # $2: windows id
    local session_name=$1
    local windows_id=$2
    local run_time=""
    local map_density=""
    local total_execs=""
    local total_paths=""
    local new_edges_on=""
    local i=""
    local content=`tmux capture-pane -pS- -t "$session_name:$windows_id"`
    run_time=`      echo "$content" | grep "run time :"       | tail -1       | sed "s/^.*run time : //g"       | sed "s/ *x.*\$//g"`
    map_density=`   echo "$content" | grep "map density :"    | tail -1       | sed "s/^.*map density : //g"    | sed "s/ *x.*\$//g"`
    total_execs=`   echo "$content" | grep "total execs :"    | tail -1       | sed "s/^.*total execs : //g"    | sed "s/ *x.*\$//g"`
    total_paths=`   echo "$content" | grep "total paths :"    | tail -1       | sed "s/^.*total paths : //g"    | sed "s/ *x.*\$//g"`
    new_edges_on=`  echo "$content" | grep "new edges on :"   | tail -1       | sed "s/^.*new edges on : //g"   | sed "s/ *x.*\$//g"`
    now_processing=`echo "$content" | grep "now processing :" | tail -1       | sed "s/^.*now processing : //g" | sed "s/ *x.*\$//g"`
    cycles_done=`   echo "$content" | grep "cycles done :"    | tail -1       | sed "s/^.*cycles done : //g"    | sed "s/ *x.*\$//g"`
    total_crashes=` echo "$content" | grep "total crashes :"  | tail -1       | sed "s/^.*total crashes : //g"  | sed "s/ *(.*\$//g"`

    if [[ ! -z $run_time ]] && [[ ! -z $map_density ]] && [[ ! -z $total_execs ]] && [[ ! -z $total_paths ]] && [[ ! -z $new_edges_on ]]
    then
	windows_name=`tmux list-windows -t $session_name | grep "^$windows_id:" | sed "s/(.*\$//g"`
	echo "$session_name;$windows_name;$run_time;$map_density;$total_execs;$total_paths;$new_edges_on;$now_processing;$cycles_done;$total_crashes"
    fi
}

# show_content_by_tmux_session() {
# }

get_all_tmux_session__array() {
    local x=`tmux ls`
    local y=""
    local i=""
    readarray -t y <<<"$x"
    for (( i=0; i<${#y[@]}; ++i ))
    do
	y[$i]=`echo ${y[$i]} | sed "s/:.*\$//g"`
    done
    ret_value=("${y[@]}")
}

get_windows_indexs_by_session_name__array() {
    local session_name=$1
    local x=`tmux list-windows -t "$session_name"`
    local y=""
    local i=""
    readarray -t y <<<"$x"
    for (( i=0; i<${#y[@]}; ++i ))
    do
	y[$i]=`echo ${y[$i]} | sed "s/:.*\$//g"`
    done
    ret_value=("${y[@]}")
}

get_all_tmux_session__array
sessions_array=("${ret_value[@]}")

for (( i=0; i<${#sessions_array[@]}; ++i ))
do
    current_session_name=${sessions_array[$i]}
    get_windows_indexs_by_session_name__array "$current_session_name"
    windows_array=("${ret_value[@]}")
    for (( j=0; j<${#windows_array[@]}; ++j ))
    do
	current_windows_id=${windows_array[$j]}
	show_content_by_tmux_session_and_windows_id "$current_session_name" "$current_windows_id"
    done
done
