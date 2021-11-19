#!/bin/bash

### settings
mysql_bin_path="/usr/local/mysql/bin/"
default_datadir="/home/fuboat/mariadb-tmp/mysql-default-data/"
instance_dir="/home/fuboat/mariadb-tmp"
instance_flag_dir="/home/fuboat/mariadb-tmp"
max_instance=10

### variable
cur_instance=""
cur_instance_port=""

### config
set -x

waiting_db_start() {
  port="$1"

  while ! $mysql_bin_path/mysqladmin ping -u root --port "$port" --socket="/tmp/$cur_instance".socket
  do
    echo "Waiting DB starting..."
    sleep 0.5
  done
}

waiting_db_close() {
  port="$1"

  $mysql_bin_path/mysqladmin shutdown -u root --port "$port" --socket="/tmp/$cur_instance".socket
}

kill_db_force() {
  local cur_data_dir="$instance_dir"/"$cur_instance"
  kill -9 "$(cat "$cur_data_dir/fuckpid.pid")"
}

start_instance() {
  local cur_data_dir="$instance_dir"/"$cur_instance"
  $mysql_bin_path/mysqld --port "$cur_instance_port" --datadir="$cur_data_dir" --socket="/tmp/$cur_instance".socket --log-error=fuckerr.err --pid-file=fuckpid.pid --disable-log-bin --core-file &
}

run_statement() {
  statement_file_path="$1"
  $mysql_bin_path/mysql  --socket="/tmp/$cur_instance".socket -u root --port "$cur_instance_port" test1 < "$statement_file_path" || echo "Crash!"
  sleep 10
}

generate_default() {
  if [[ ! -d "$default_datadir" ]]
  then
    waiting_db_close 3306

    mkdir "$default_datadir"
    $mysql_bin_path/../scripts/mysql_install_db --auth-root-authentication-method=normal --datadir="$default_datadir"
    $mysql_bin_path/mysqld --datadir="$default_datadir" --log-error=fuckerr.err --pid-file=fuckpid.pid --disable-log-bin --socket="/tmp/$cur_instance".socket &

    waiting_db_start 3306

    echo "create database fuck; create database test1;" | $mysql_bin_path/mysql -u root --socket="/tmp/$cur_instance".socket

    waiting_db_close 3306
  fi
}

copy_default() {
  if [[ ! -d "$default_datadir" ]]
  then
    generate_default
  fi

  if [[ ! -d "$instance_dir" ]]
  then
    mkdir "$instance_dir"
  fi

  rm -rf "${ins tance_dir:?}"/"$cur_instance"
  cp -r "$default_datadir" "$instance_dir"/"$cur_instance"
}

prepare() {
  #
  # Waiting a available mysqld instance.
  #

  cur_instance=0

  for (( cur_instance=0;;cur_instance=(cur_instance+1)%max_instance ))
  do
    # If this dir not exists, it means the instance #cur is available.
    # In this condition, we do mkdir to dominate the instance #cur and break.

    lockfile -r 0 "$instance_flag_dir/instance_flag_$cur_instance" && break

    if (( cur_instance==max_instance-1 ))
    then
      sleep 5
    fi
  done

  (( cur_instance_port=10000+cur_instance ))

  copy_default
}

free() {
  #
  # free the mysqld instance.
  #

  rm -f "$instance_flag_dir/instance_flag_$cur_instance"
}

get_statement_run_log() {
  statement_file_path="$1"

  prepare
  start_instance
  waiting_db_start "$cur_instance_port"
  run_statement "$statement_file_path"
  kill_db_force
}

export LSAN_OPTIONS=detect_leaks=0
get_statement_run_log "$1"
cat "$instance_dir/$cur_instance/fuckerr.err" > "$2"
echo -e "\nbt" | gdb "$mysql_bin_path/mysqld" "$instance_dir/$cur_instance/"core* >> "$2"
free
