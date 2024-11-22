#!/bin/bash -ex
#
# Check all Python files for coding style/correctness.

pep8 --max-line-length=420 --repeat ../../../yam/ ../../../pyam ../../../setup.py ../../../pyam-block-until-release ../../../pyam-build
