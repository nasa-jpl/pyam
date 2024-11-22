#!/bin/bash

# Confirm that sql_database_reader does not write to the database
filename='../../../yam/sql_database_reader.py'

for substring in 'INSERT' 'UPDATE' 'DELETE' 'CREATE' 'DROP' 'ALTER' 'INDEX'
do
    echo "Searching for $substring"
    found_line=$(../../common/token/find_token.py --word "$substring" "$filename")
    if [ $? -eq 0 ]
    then
            echo
            echo "ERROR: Found line '$found_line' in '$filename', which indicates writing to database. DatabaseReader should only read from the database."
            exit 2
    fi
done

echo 'OK'
