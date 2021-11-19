#!/bin/bash

### settings
mysql_bin_path="/root/bin_original/usr/local/mysql/bin/"

### variable
cur_instance=""
cur_instance_port=""

datadir=""
socket=""
log_err_file=""
pid_file=""
port=""
user=""
password=""

### config
set -x

waiting_db_start() {
  while ! $mysql_bin_path/mysqladmin ping --user="$user" --password="$password" --port="$port" --socket="$socket"
  do
    echo "Waiting DB starting..."
    sleep 0.5
  done
}

waiting_db_close() {
  $mysql_bin_path/mysqladmin shutdown --user="$user" --password="$password" --port="$port" --socket="$socket"
}

kill_db_force() {
  kill -9 $(cat "$pid_file")
}

start_instance() {
    $mysql_bin_path/mysqld --user="$user" --port="$port" --datadir="$datadir" \
			   --socket="$socket" --log-error="$log_err_file" --pid-file="$pid_file" \
			   --disable-log-bin &
}

generate_default() {
  if [[ ! -d "$datadir" ]]
  then
    mkdir "$datadir"
    $mysql_bin_path/../scripts/mysql_install_db --auth-root-authentication-method=normal --datadir="$datadir"
  fi
}

usage() {
    echo "\
Usage: $0 \
-d <datadir> -s <socket-file> -l <log-error-file> -i <pid-file> \
-P <port-number> -u <username> -p <password>"
    exit 1
}

while getopts ":d:s:l:i:P:u:p:" o
do
    case "${o}" in
	d)
	    datadir="${OPTARG}"
	    ;;
	s)
	    socket="${OPTARG}"
	    ;;
	l)
	    log_err_file="${OPTARG}"
	    ;;
	i)
	    pid_file="${OPTARG}"
	    ;;
	P)
	    port="${OPTARG}"
	    ;;
	u)
	    user="${OPTARG}"
	    ;;
	p)
	    password="${OPTARG}"
	    ;;
    esac
done

if [ -z "${datadir}" ] || [ -z "${socket}" ] || [ -z "${log_err_file}" ] || \
       [ -z "${pid_file}" ] || [ -z "${port}" ] || [ -z "${user}" ]
then
    usage
fi

generate_default
start_instance
waiting_db_start
