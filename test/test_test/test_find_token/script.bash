#!/bin/bash
#
# Test the find_token.py utility.

../../common/token/find_token.py --keyword 'global' foo.py > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: keyword "global" should have been found in foo.py'
    exit 2
else
    echo -n '.'
fi

../../common/token/find_token.py --keyword 'global' foobar.py > /dev/null
if [ $? -eq 0 ]
then
    echo 'ERROR: keyword "global" should not have been found in foobar.py'
    exit 2
else
    echo -n '.'
fi

../../common/token/find_token.py --keyword 'for' foo.py > /dev/null
if [ $? -eq 0 ]
then
    echo 'ERROR: keyword "for" should not have been found'
    exit 2
else
    echo -n '.'
fi

../../common/token/find_token.py --keyword 'if' foobar.py > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: keyword "if" should have been found'
    exit 2
else
    echo -n '.'
fi

../../common/token/find_token.py --name 'execfile' foobar.py > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: name "execfile" should have been found'
    exit 2
else
    echo -n '.'
fi

../../common/token/find_token.py --word 'my string' foo.py > /dev/null
if [ $? -eq 0 ]
then
    echo 'ERROR: "my string" should have failed since it is not a word'
    exit 2
else
    echo -n '.'
fi

../../common/token/find_token.py --word 'bc' foo.py > /dev/null
if [ $? -eq 0 ]
then
    echo 'ERROR: string "bc" should have not been found since it is not a full match'
    exit 2
else
    echo -n '.'
fi

../../common/token/find_token.py --word 'my_sTriNg' foo.py > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: string "my_sTriNg" should have been found'
    exit 2
else
    echo -n '.'
fi

../../common/token/find_token.py --word 'my_string' foo.py > /dev/null
if [ $? -eq 0 ]
then
    echo 'ERROR: string "my_string" should not have been found'
    exit 2
else
    echo -n '.'
fi

../../common/token/find_token.py --word '123blahblah' foo.py > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: string "123blahblah" should have been found'
    exit 2
else
    echo -n '.'
fi

echo
echo 'OK'
