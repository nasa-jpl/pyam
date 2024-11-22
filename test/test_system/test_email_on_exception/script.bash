#!/bin/bash
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
    kill "$smtp_server_pid"
}


# Start SMTP server
../../common/email/file_printing_smtp_server.py "$email_port_filename" "$email_dump_filename" &
smtp_server_pid=$!
# Wait for server to start
while true
do
    if [ -e "$email_port_filename" ]
    then
        SMTP_PORT=$(cat "$email_port_filename")
        break
    fi
done


# Start actual script
export YAM_SEND_EXCEPTION_TO_HOST_PORT_EMAIL="localhost:$SMTP_PORT:fake.email@sdfsdffsdfsfsdfs.com"

# Make pyam not able to find package.
cp ../../../pyam .

output=$(./pyam --version 2>&1)

rm -f pyam

# Extract the log filename from the error message
log_filename=$(echo "$output" | grep 'pyam_crash' | sed "s/.*'\(.*\)'.*/\1/")
rm -f "$log_filename"

# Make sure the email was sent
if [ ! -s "$email_dump_filename" ]
then
    echo "ERROR: Email dump file should exist at $email_dump_filename"
    exit 2
fi

grep 'From:' "$email_dump_filename" > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: "From:" line should exist in email'
    exit 2
fi

grep 'Subject: pyam crash' "$email_dump_filename" > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: "Subject: pyam crash" line should exist in email'
    exit 2
fi

rm -f "$email_dump_filename"

echo 'OK'
