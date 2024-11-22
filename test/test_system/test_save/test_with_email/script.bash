#!/bin/bash -ex
#
# Start the SMTP server then start the test.

email_port_filename=$(readlink -f './email_port_file')
email_dump_filename=$(readlink -f './email_dump_file')

rm -f "$email_port_filename"
rm -f "$email_dump_filename"


trap stop_smtp_server EXIT
stop_smtp_server()
{
    rm -f "$email_port_filename"
    kill $smtp_server_pid
}


# Start SMTP server
../../../common/email/file_printing_smtp_server.py "$email_port_filename" "$email_dump_filename" &
smtp_server_pid=$!
# Wait for server to start
while true
do
    if [ -e "$email_port_filename" ]
    then
        SMTP_PORT=$(cat "$email_port_filename")
        break
    else
        sleep 1
    fi
done


# Start actual script
export SMTP_PORT
./internal.bash

echo
echo 'OK'
