#!/bin/bash -ex
#
# Run on Jenkins CI.

tox

rm -rf ./distribution
./distribute.bash ./distribution
cd ./distribution
tar xf pyam*.tar.gz
cd pyam*[0-9]
./standalone.bash ./foo
./foo/bin/pyam --help
