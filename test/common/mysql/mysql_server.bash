#!/bin/bash

# Function for starting a MySQL with a known state.

MYSQL_SOCKET=""
MY_TMP_DIR=""

curdir=`pwd`
basenm=`basename $curdir`

# Echo to stderr to avoid polluting stdout
echo_verbose()
{
    echo "$@" 1>&2
}

get_available_port()
{
    local lowest_port=10000
    local highest_port=49151
    local offset="$RANDOM"
    for index in $(seq $lowest_port $highest_port)
    do
        local port=$(((offset + index) % highest_port + lowest_port))
        nmap -Pn -p "$index" 127.0.0.1 | grep closed >& /dev/null
        if [ $? -eq 0 ]
        then
            echo "$port"
            return 0
        fi
    done
    return 1
}

# Starts a MySQL server at a random available port.
# Sets global variable START_MYSQL_SERVER_RETURN_PORT to return port value.
#
# sql_filename - location of SQL data, which will be imported by the server
# verbose - if enabled, verbose messages will be printed to stderr
start_mysql_server()
{
    local sql_filename=$1
    local verbose=$2

    # Seed the random number generator (used in get_available_port())
    RANDOM=$(date +%s)

    # mysql_data_dir must be an absolute path due to mysqld's requirement
    # Temporary directory is not placed in the working directory as MySQL will complain about the socket path being too long.
    MY_TMP_DIR=$(mktemp --directory)
    # echo "XXXXXX $MY_TMP_DIR"

    mysql_data_dir="$MY_TMP_DIR/mysql_data_$basenm"
    mkdir "$mysql_data_dir"

    if [ -n "$verbose" ]
    then
        echo_verbose '* Setting up MySQL data'
        echo_verbose '* Waiting for mysqld to start'
    fi

    # Allow multiple retries to decrease chance of failing due to race
    # condition in choosing available port.
    local wait_index=0
    local wait_index_at_last_launch_attempt=0
    local mysqld_touch_file_on_exit="$mysql_data_dir/mysqld_exited"
    touch "$mysqld_touch_file_on_exit"
    while true
    do
        # Try starting process if we haven't tried yet or if the previous try
        # failed. Processes may die due to port collision during a race.
        if [ -e "$mysqld_touch_file_on_exit" ]
        then
            if [ -n "$verbose" ]
            then
                echo -n '* '
            fi

            rm -f "$mysqld_touch_file_on_exit"

            # Clean up data directory as previous failure may have been due to
            # corrupt data.
            rm -rf "$mysql_data_dir"/*

            mysql_install_db --ldata="$mysql_data_dir" --user="$USER" --auth-root-authentication-method=normal &> /dev/null
            MYSQL_SOCKET="$mysql_data_dir/mysql.sock"

            rm -f "$MYSQL_SOCKET"
            rm -f "$mysql_data_dir/mysql.pid"

            local port=$(get_available_port)

            # If mysqld exits, we will touch a file so that we know of the
            # failure. We run it in a separate process and echo the output so
            # that (expected) errors don't pollute our standard out.
            echo $(\
                /usr/libexec/mysqld \
                --no-defaults \
                --sql-mode=STRICT_ALL_TABLES \
                --tmpdir="$MY_TMP_DIR" \
                --datadir="$mysql_data_dir" \
                --port="$port" \
                --pid-file="$mysql_data_dir/mysql.pid" \
                --socket="$MYSQL_SOCKET" 2>&1; \
                touch "$mysqld_touch_file_on_exit" 2>&1) >> \
                "$mysql_data_dir/mysqld_error_output" &

            wait_index_at_last_launch_attempt=$wait_index
        fi

        if [ -S "$MYSQL_SOCKET" ]
        then
            # Check if the server is ready. If so, break out of loop.
            mysqladmin --user=root --socket="$MYSQL_SOCKET" ping &> /dev/null
            if [ $? -eq 0 ]
            then
                # For some reason the connection sometimes still fails. Be extra sure that
                # the server will work by running the actual Python mysql command that
                # SQLDatabase uses.
                python -c "from mysql import connector; c = connector.connect(host='127.0.0.1', user='', password='', port=$port, database='test'); c.close()" &> /dev/null
                if [ $? -eq 0 ]
                then
                    break
                fi
            fi
        fi

        # If we've waited a 30 seconds since the last try, give up on the
        # current mysqld process and try again.
        if [ -e "$mysql_data_dir/mysql.pid" ]
        then
            if [ $((wait_index - wait_index_at_last_launch_attempt)) -gt 300 ]
            then
                # Kill the mysqld process
                kill -9 $(cat "$mysql_data_dir/mysql.pid")
                sleep 1

                # Write mysqld output to file for debugging if we wait too long
                if [ $wait_index -gt 1200 ]
                then
                    cat "$mysql_data_dir/mysqld_error_output" > "retrying-$(hostname)-$(date +%s)"
                fi
            fi
        fi

        # Quit trying after 16 minutes
        if [ $wait_index -gt 9600 ]
        then
            echo 'ERROR: Could not start MySQL server'
            cat "$mysql_data_dir/mysqld_error_output"
            exit 2
        fi

        if [ -n "$verbose" ]
        then
            echo -n '.'
        fi

        let wait_index=$wait_index+1
        sleep .1
    done

    if [ -n "$verbose" ]
    then
        echo
    fi

    # Taken from: https://gist.github.com/mattolenik/bb2e206a36a4f98121695c25e53a1e7e
    # appends a command to a trap
    #
    # - 1st arg:  code to add
    # - remaining args:  names of traps to modify
    #
    trap_add() {
        trap_add_cmd=$1; shift || fatal "${FUNCNAME} usage error"
        for trap_add_name in "$@"; do
            trap -- "$(
                # helper fn to get existing trap command from output
                # of trap -p
                extract_trap_cmd() { printf '%s\n' "$3"; }
                # print existing trap command with newline
                eval "extract_trap_cmd $(trap -p "${trap_add_name}")"
                # print the new trap command
                printf '%s\n' "${trap_add_cmd}"
            )" "${trap_add_name}" \
                || fatal "unable to add to trap ${trap_add_name}"
        done
    }

    # Run stop_mysql_server on EXIT. We use trap_add here to append this to any existing
    # trap commands rather than totally overwrite them.
    trap_add stop_mysql_server EXIT

    stop_mysql_server()
    {
        if [ -n "$MYSQL_SOCKET" ]
        then

            #mysqldump --user=root --socket="$MYSQL_SOCKET" --all-databases > "$MY_TMP_DIR/all.dump"
            kill -SIGTERM $(cat "$mysql_data_dir/mysql.pid")

            # Wait until background process completes before trying to delete
            # the data directory.
            wait

            rm -rf "$MY_TMP_DIR"
        fi
    }

    if [ -n "$sql_filename" ]
    then
        # Import tables with known state
        if [ -n "$verbose" ]
        then
            echo_verbose '* Importing database'
        fi
        mysql --socket="$MYSQL_SOCKET" --user="$USER" test < "$sql_filename"
    fi

    if [ -n "$verbose" ]
    then
        echo_verbose '* MySQL server ready'
    fi

    START_MYSQL_SERVER_RETURN_PORT=$port
}


start_read_only_mysql_server()
{
    if [ $# -lt 1 ]
    then
        echo "Usage: start_read_only_mysql_server sql_data_file"
        exit 1
    fi
    local sql_filename=$1

    echo "$sql_filename" | grep 'example_yam_for_import.sql' > /dev/null
    if [ $? -ne 0 ]
    then
        echo 'This script is meant for running a single global read-only server. Thus we expect it to use the same file "example_yam_for_import.sql"'
        exit 1
    fi

    # Start a new server if it hasn't been started previously. We indicate a
    # previously started server by setting environment variable
    # "READ_ONLY_MYSQL_SERVER_PORT".
    if [ -z "$READ_ONLY_MYSQL_SERVER_PORT" ]
    then
        start_mysql_server "$sql_filename"

        export READ_ONLY_MYSQL_SERVER_PORT=$START_MYSQL_SERVER_RETURN_PORT

        # Set read-only mode.
        mysql -h 127.0.0.1 --user="root" --password="" --port="$READ_ONLY_MYSQL_SERVER_PORT" test << EOF
        SET GLOBAL read_only = ON;
EOF
        if [ $? -ne 0 ]
        then
            echo 'Setting MySQL read-only mode failed.'
            exit 2
        fi
    fi
}
