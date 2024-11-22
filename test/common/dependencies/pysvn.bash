#!/bin/bash -ex
#
# Install via script for virtualenv usage. This is necessary because pysvn does
# not install correctly under pip.

readonly prefix=$(python -c \
    'from distutils import sysconfig; print(sysconfig.get_python_lib(standard_lib=False))')

if [ -f "$prefix/pysvn/__init__.py" ]
then
    exit
fi

readonly pysvn='pysvn-1.8.0'
curl --retry 10 -o "$pysvn.tar.gz" \
    "http://pysvn.barrys-emacs.org/source_kits/$pysvn.tar.gz"

rm -rf "$pysvn"
tar xf "$pysvn.tar.gz"

cd "$pysvn/Source"
python setup.py configure
make

mkdir -p "$prefix/pysvn"
cp pysvn/__init__.py "$prefix/pysvn/"
cp pysvn/_pysvn*.so "$prefix/pysvn/"
