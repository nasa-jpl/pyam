#!/bin/bash -x

# Unset YAM_ROOT or it will interfere.
# Makefile.yam will pick up the real sandbox that contains the pyam module.
unset YAM_ROOT

# Unset configuration file environment variables as they may interfere.
unset YAM_PROJECT_CONFIG_DIR
unset YAM_PROJECT

# Don't email exception.
unset YAM_SEND_EXCEPTION_TO_HOST_PORT_EMAIL

# Make pyam not able to find package.
cp ../../../pyam .

output=$(./pyam --version 2>&1)

rm pyam

# Extract the log filename from the error message.
log_filename=$(echo "$output" | grep 'pyam_crash' | sed "s/.*'\(.*\)'.*/\1/")

# Determine the log filename
if [ -s "$log_filename" ]
then
    echo 'OK'
else
    echo "ERROR: Log file '$log_filename' is either empty or missing. It should contain a pyam error log. See below for output of pyam."
    echo "$output"
    exit 2
fi

rm -f "$log_filename"
