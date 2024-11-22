#!/bin/bash -ex
#
# Check Make-related Python files for spelling errors.

# Test Make-related module separately since it contains non-word strings.
./check_spelling.py --word-list='make_exceptions.txt' ../../../yam/make_build_system.py
