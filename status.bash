#!/bin/bash
#
# List files that need improvement.

failed=false
for filename in $(find ./yam -name '*.py') './pyam'
do
    for keyword in 'FIXME' 'HACK' 'TODO'
    do
        grep -i --with-filename --color=auto "$keyword" "$filename"
        if [ $? -eq 0 ]
        then
            failed=true
        fi
    done
done

if ! $failed
then
    echo 'OK'
fi
