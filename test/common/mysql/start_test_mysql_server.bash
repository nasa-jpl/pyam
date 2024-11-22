#!/bin/bash
#
# Start a MySQL server for testing purposes.
#
# Test files will be created in a temporary directory

options=':i:er:s:'

printUsage()
{
    if ( ! getopts "$options" opt) then
        echo "usage: $0 [-e] [-i DATABASE_NAME] [-r READY_INDICATION_FILENAME] [-s SQL_FILNAME]"
        echo
        echo 'required arguments:'
        echo '  -r READY_INDICATION_FILENAME'
        echo "                        write a file at this location that will contain the server's network port"
        echo
        echo 'optional arguments:'
        echo '  -e                    exit immediately after starting server'
        echo '  -i DATABASE_NAME      start an interactive MySQL client after starting the server'
        echo '  -s SQL_FILNAME        read this SQL dump after starting server'
    fi
}

while getopts "$options" opt; do
    case $opt in
        e)
            exit_immediately=true >&2
            ;;
        i)
            interactive="$OPTARG" >&2
            ;;
        r)
            ready_indication_filename="$OPTARG" >&2
            ;;
        s)
            sql_filename="$OPTARG" >&2
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            exit 1
            ;;
    esac
done

if [ -z "$ready_indication_filename" ]
then
    printUsage
    echo 'Option -r must be specified (with an argument).'
    exit 1
fi

if [ -n "$interactive" ]
then
    if [ -n "$exit_immediately" ]
    then
        echo 'Option -e cannot be used with -i.'
        exit 1
    fi
fi

resolved_file_path="`readlink -f \"$0\"`"
dir_name="`dirname $resolved_file_path`"
source "$dir_name/mysql_server.bash"

start_mysql_server "$sql_filename" 'verbose'
port=$START_MYSQL_SERVER_RETURN_PORT

# Write port to temporary file and then do a hopefully atomic move.
# The atomic move is necessary otherwise the client process may end up reading
# a partial file.
# We put the temporary file in the same directory as the final file so that the
# move is atomic.
directory_of_ready_file=$(dirname "$ready_indication_filename")
temporary_ready_filename=$(mktemp --tmpdir="$directory_of_ready_file")
echo $port >> "$temporary_ready_filename"
mv "$temporary_ready_filename" "$ready_indication_filename"

if [ -n "$interactive" ]
then
    mysql -h 127.0.0.1 --user="" --password="" --port=$port "$interactive"
else
    # Sleep until we are killed
    while [ -z "$exit_immediately" ]
    do
        sleep 1
    done
fi
