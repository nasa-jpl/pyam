#!/bin/bash
#
# Test loading configuration file based on environment variables.

export YAM_PROJECT_CONFIG_DIR='fake_configuration_directory'
export YAM_PROJECT='FakeProject'

# Unset YAM_ROOT or it will interfere.
# Makefile.yam will pick up the real sandbox that contains the pyam module.
unset YAM_ROOT

output=$(../../../../pyam --help)
echo "$output" | grep '(default: 127.0.0.1:54321:fake:fake:fake)' > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: Default argument for --no-build-server --database-connection was not read from configuration file'
    echo "$output"
    exit 2
fi

echo "$output"  | grep "(default: fake_repo_url)" > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: Default argument for --default-repository-url was not read from configuration file'
    echo "$output"
    exit 2
fi

echo "$output"  | grep "(default: 1.2.1)" > /dev/null
if [ $? -ne 0 ]
then
    echo 'ERROR: Default argument for --repository-version was not read from configuration file'
    echo "$output"
    exit 2
fi

echo 'OK'
