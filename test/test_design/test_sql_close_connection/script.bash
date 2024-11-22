#!/bin/bash

# Confirm that each SQLDatabase connection is closed using Python's context manager syntax.
for filename in ../../../yam/*sql*.py
do
    num_connect_calls=$(grep 'connect(' "$filename" | wc -l)
    num_cursor_calls=$(grep 'cursor()' "$filename" | wc -l)
    num_closing=$(grep 'closing(' "$filename" | wc -l)
    num_close=$(grep 'connection\.close(' "$filename" | wc -l)
    if [ $((num_connect_calls+num_cursor_calls)) -ne $((num_closing+num_close)) ]
    then
            echo
            echo "ERROR: Number of MySQL connect calls ($num_connect_calls) plus number of cursor creations ($num_cursor_calls) does not match number of closing statements ($num_closing)."
            exit 2
    fi
done

echo 'OK'
