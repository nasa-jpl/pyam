#!/bin/bash -ex
#
# Check all Python files for commented out code.
# Code should not be commented out as it litters the code and makes it harder to
# read. Instead, simply delete it. Keeping a history is done by the revision
# control system.

./check_for_commented_out_code.py `find '../../../yam' -name '*.py' ` '../../../pyam'
