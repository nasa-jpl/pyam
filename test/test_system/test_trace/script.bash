#!/bin/bash -x

# Unset YAM_ROOT or it will interfere.
# Makefile.yam will pick up the real sandbox that contains the pyam module.
unset YAM_ROOT

# Unset configuration file environment variables as they may interfere.
unset YAM_PROJECT_CONFIG_DIR
unset YAM_PROJECT

# Run with trace enabled
yam_trace_to_log='pyam_trace.log'
rm -f "$yam_trace_to_log"
output=$(python -m trace --trace ../../../pyam --help > "$yam_trace_to_log")

# Check that trace log exists
if [ ! -s "$yam_trace_to_log" ]
then
    echo "ERROR: Trace log '$yam_trace_to_log' is either empty or missing. It should contain a pyam trace log. See below for output of pyam."
    echo "$output"
    exit 2
fi

# Make sure it contains actual content
grep 'pyam(' "$yam_trace_to_log" > /dev/null
if [ $? -ne 0 ]
then
    echo "ERROR: Log log '$yam_trace_to_log' does not contain any lines that start with 'pyam(:'"
    exit 2
fi

# Make sure there is mention of yam package.
grep '\<yam\>' "$yam_trace_to_log" > /dev/null
if [ $? -ne 0 ]
then
    echo "ERROR: Log log '$yam_trace_to_log' does not contain any lines referring to yam package"
    exit 2
fi

rm -f "$yam_trace_to_log"

echo 'OK'
