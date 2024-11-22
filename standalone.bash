#!/bin/bash -eux
#
# Install pyam and all dependencies in a standalone directory.
#
# This requires the GNU toolchain. This will install Python, Subversion,
# mysql-python-connector, and pyam
#
# Note that the output directory should not be moved. Otherwise, shebang lines
# will continue to point to the old location. And library paths may not match.
#
# Relevant environment variables are below.
#
# - STANDALONE_CURL_OPTIONS
# - STANDALONE_IGNORE_SHASUM
# - STANDALONE_USE_SUBVERSION_1_6
# - STANDALONE_USE_SYSTEM_SQLITE
# - STANDALONE_USE_SYSTEM_SUBVERSION

# ignore shasum since the sha extensions are variable
export STANDALONE_IGNORE_SHASUM=1

readonly jobs=$( \
    python \
    -c 'import multiprocessing; print(multiprocessing.cpu_count())' 2> \
    /dev/null || \
    echo 2)


download()
{
    # Running curl multiple tries since "--retry" does not seem to catch all
    # problems.
    local count=0
    while true
    do
        if [ $count -gt 3 ]
        then
            echo 'Timed out' >&2
            exit 1
        fi

        let count=$count+1

        if [ -v STANDALONE_CURL_OPTIONS ]
        then
            local -r curl_command="curl $STANDALONE_CURL_OPTIONS"
        else
            # local -r curl_command='curl'
            local curl_command='curl'
        fi

        # shellcheck disable=SC2086
        $curl_command --retry 10 --location --output "$1" "$2" || continue

#         if [ ! -v STANDALONE_IGNORE_SHASUM ]
#         then
#             #            if shasum --check "$script_directory/standalone/$1.sha1"
#             if shasum --check "$script_directory/standalone/$1.sha512"
#             then
#                 break
#             fi
#         fi
    done
}


install_python()
{
    local -r output_directory="$1"

    #local -r source_directory='Python-3.4.3'
    local -r source_directory='Python-3.9.0'

    local -r original_directory="$PWD"
    mkdir -p 'standalone-temporary'
    cd 'standalone-temporary'

    if [ ! -f "$source_directory.tgz" ]
    then
        download "$source_directory.tgz" \
            'https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tgz'
    fi

    if [ ! -d "$source_directory" ]
    then
        tar xf "$source_directory.tgz"
    fi

    if [ ! -f "$output_directory/bin/python3" ]
    then
        cd "$source_directory"

        # Isolate from environment variables like "PYTHONPATH" and
        # "PYTHONHOME".
        sed \
            -e 's/^\(int Py_IgnoreEnvironmentFlag\).*;/\1 = 1;/g' \
            -i'' Python/pythonrun.c

        ./configure --prefix="$output_directory"
        make -j "$jobs" install
    fi

    cd "$original_directory"
}


install_sqlite()
{
    local -r output_directory="$1"

    #local -r source_directory='sqlite-autoconf-3080100'
    local -r source_directory='sqlite-autoconf-3330000'

    local -r original_directory="$PWD"
    mkdir -p 'standalone-temporary'
    cd 'standalone-temporary'

    if [ ! -f "$source_directory.tar.gz" ]
    then
        download \
            "$source_directory.tar.gz" \
            "https://sqlite.org/2020/$source_directory.tar.gz"
#           "https://sqlite.org/2013/$source_directory.tar.gz"
    fi

    if [ ! -d "$source_directory" ]
    then
        tar xf "$source_directory.tar.gz"
    fi

    cd "$source_directory"
    ./configure --prefix="$output_directory"
    make -j "$jobs" install

    cd "$original_directory"
}


install_apr()
{
    local -r output_directory="$1"

    #local -r source_directory='apr-1.5.0'
    local -r source_directory='apr-1.7.0'

    local -r original_directory="$PWD"
    mkdir -p 'standalone-temporary'
    cd 'standalone-temporary'

    if [ ! -f "$source_directory.tar.gz" ]
    then
        download \
            "$source_directory.tar.gz" \
            "https://archive.apache.org/dist/apr/$source_directory.tar.gz"
    fi

    if [ ! -d "$source_directory" ]
    then
        tar xf "$source_directory.tar.gz"
    fi

    cd "$source_directory"
    ./configure --prefix="$output_directory"

    # apr seems to have flaky parallel builds.
    make install

    cd "$original_directory"
}


install_apr_util()
{
    local -r output_directory="$1"

    local -r source_directory='apr-util-1.5.3'

    local -r original_directory="$PWD"
    mkdir -p 'standalone-temporary'
    cd 'standalone-temporary'

    if [ ! -f "$source_directory.tar.gz" ]
    then
        download \
            "$source_directory.tar.gz" \
            "https://archive.apache.org/dist/apr/$source_directory.tar.gz"
    fi

    if [ ! -d "$source_directory" ]
    then
        tar xf "$source_directory.tar.gz"
    fi

    cd "$source_directory"
    ./configure \
        --with-apr="$output_directory/bin/apr-1-config" \
        --with-sqlite3="$output_directory" \
        --prefix="$output_directory"

    # apr-util seems to have flaky parallel builds.
    make install

    cd "$original_directory"
}


install_subversion()
{
    local -r output_directory="$1"

    if [ -v STANDALONE_USE_SUBVERSION_1_6 ]
    then
        local -r source_directory='subversion-1.6.11'
    else
        #local -r source_directory='subversion-1.8.4'
        local -r source_directory='subversion-1.14.0'
    fi

    local -r original_directory="$PWD"
    mkdir -p 'standalone-temporary'
    cd 'standalone-temporary'

    if [ ! -f "$source_directory.tar.gz" ]
    then
        download \
            "$source_directory.tar.gz" \
            "https://archive.apache.org/dist/subversion/$source_directory.tar.gz"
    fi

    if [ ! -d "$source_directory" ]
    then
        tar xf "$source_directory.tar.gz"
    fi

    cd "$source_directory"
    ./configure \
        --with-apr="$output_directory/bin/apr-1-config" \
        --with-apr-util="$output_directory/bin/apu-1-config" \
        --with-sqlite="$output_directory" \
        --without-apxs \
        --without-doxygen \
        --without-swig \
        --prefix="$output_directory"
    make install

    cd "$original_directory"
}


install_pysvn()
{
    local -r output_directory="$1"

    local -r prefix=$( \
        "$output_directory/bin/python3" \
        -c 'from distutils import sysconfig; print(sysconfig.get_python_lib(standard_lib=False))')

    local -r original_directory="$PWD"
    mkdir -p 'standalone-temporary'
    cd 'standalone-temporary'

    #local -r pysvn='pysvn-1.7.6'
    local -r pysvn='pysvn-1.9.10'
    if [ ! -d "$pysvn.tar.gz" ]
    then
        download \
            "$pysvn.tar.gz" \
            "http://pysvn.barrys-emacs.org/source_kits/$pysvn.tar.gz"
    fi

    rm -rf "$pysvn"
    tar xf "$pysvn.tar.gz"

    cd "$pysvn/Source"

    if [ -v STANDALONE_USE_SYSTEM_SUBVERSION ]
    then
        "$output_directory/bin/python3" setup.py configure
    else
        "$output_directory/bin/python3" setup.py configure \
            --apr-inc-dir="$output_directory/include/apr-1" \
            --apu-inc-dir="$output_directory/include/apr-1" \
            --apr-lib-dir="$output_directory/lib" \
            --svn-root-dir="$output_directory"
    fi
    make

    mkdir -p "$prefix/pysvn"
    cp pysvn/__init__.py "$prefix/pysvn/"
    cp pysvn/_pysvn*.so "$prefix/pysvn/"

    cd "$original_directory"
}


install_python_package_tarball()
{
    local -r output_directory="$1"
    local -r name="$2"
    local -r base_url="$3"

    local -r original_directory="$PWD"
    mkdir -p 'standalone-temporary'
    cd 'standalone-temporary'

    if [ ! -d "$name.tar.gz" ]
    then
        download "$name.tar.gz" "$base_url/$name.tar.gz"
    fi

    rm -rf "$name"
    tar xf "$name.tar.gz"

    cd "$name"
    #"$output_directory/bin/python3" setup.py install
    "$output_directory/bin/python" setup.py install

    cd "$original_directory"
}

install_python_package()
{
    local -r output_directory="$1"
    local -r url="$2"

    #"$output_directory/bin/python3" setup.py install
    "$output_directory/bin/pip3" install $url
}


install_pyam()
{
    local -r output_directory="$1"

    cd "$script_directory"
    "$output_directory/bin/python3" setup.py install
}


# set these variables to 0 to disable specific installation steps
build_sqlite=1
build_subversion=1
build_python=1
build_python_extras=1
build_pyam=1
build_argcomplete=1

main()
{
    # Get absolute path.
    local -r old_path="$PWD"
    cd "$raw_output_directory"
    local -r output_directory="$PWD"
    cd "$old_path"

    if [ $build_sqlite != 0 ]
       then
       if [ ! -v STANDALONE_USE_SYSTEM_SQLITE ]
       then
           install_sqlite "$output_directory"
       fi
    fi

    if [ $build_subversion != 0 ]
       then
       if [ ! -v STANDALONE_USE_SYSTEM_SUBVERSION ]
       then
           install_apr "$output_directory"
           install_apr_util "$output_directory"
           install_subversion "$output_directory"
       fi
    fi

    export PYTHONHOME="$output_directory"
    if [ $build_python != 0 ]
       then
           install_python "$output_directory"


    fi
    #        'setuptools-15.2' \

    if [ $build_python_extras != 0 ]
       then
           install_python_package \
               "$output_directory" \
               "https://files.pythonhosted.org/packages/a7/e0/30642b9c2df516506d40b563b0cbd080c49c6b3f11a70b4c7a670f13a78b/setuptools-50.3.2.zip"

               #'setuptools-50.3.2' \
               #'https://pypi.python.org/packages/source/s/setuptools'
           install_python_package \
               "$output_directory" \
               "https://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-1.1.6.tar.gz"

               #'mysql-connector-python-1.1.6' \
               #'https://dev.mysql.com/get/Downloads/Connector-Python'

           install_python_package \
               "$output_directory" \
               "http://pysvn.barrys-emacs.org/source_kits/pysvn-1.9.10.tar.gz"


           #install_pysvn "$output_directory"
    fi

    if [ $build_pyam != 0 ]
       then
           # $output_directory/bin/pip3 install dateutil

           install_python_package \
               "$output_directory" \
               "https://files.pythonhosted.org/packages/73/30/e9e22e80fc592803edb23d89588ccaa184f14bb67d9c321f705edbfdd95b/py-dateutil-2.2.tar.gz"
           install_pyam "$output_directory" "$script_directory"
    fi

    if [ $build_argcomplete != 0 ]
       then
           install_python_package \
               "$output_directory" \
               "https://pypi.python.org/packages/source/a/argcomplete/argcomplete-1.12.1.tar.gz"

               #'argcomplete-1.12.1' \
               #'https://pypi.python.org/packages/source/a/argcomplete'
    fi

#        'argcomplete-0.8.8' \

    echo "Add '$output_directory/bin' to then your PATH"
}


if [ $# -ne 1 ]
then
    echo "Usage: $0 output_directory"
    exit 1
fi

readonly resolved_file_path=$(readlink -f "$0")
readonly script_directory=$(dirname "$resolved_file_path")

readonly raw_output_directory="$1"
mkdir -p "$raw_output_directory"


main
