#!/bin/bash -ex
#
# Check all Python files for coding style/correctness.

pyflakes ../../../yam/*.py ../../../pyam ../../../setup.py ../../../pyam-block-until-release ../../../pyam-build
