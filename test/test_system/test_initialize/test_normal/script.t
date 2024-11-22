Test "initialize" command.

Check make version is >= 4.4. If not, then we need to ignore the jobserver warnings.
    $ MAKE_VERSION=$(make --version | grep -i -c -E "GNU Make ([4-9]\.[4-9])")

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

This will not exist until after "pyam initialize".

    $ release_directory="$CRAMTMP/fake_release"

Start empty MySQL server.

    $ . "$TESTDIR/../../../common/mysql/mysql_server.bash"
    $ start_mysql_server '/dev/null'
    $ PORT=$START_MYSQL_SERVER_RETURN_PORT

Create fake SVN repository.

    $ fake_repository_path="$CRAMTMP/fake_repository"
    $ svnadmin create "$fake_repository_path"
    $ fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"

    $ PYAM="$TESTDIR/../../../../pyam --quiet --non-interactive --site=telerobotics --no-build-server --database-connection=127.0.0.1:$PORT/test --release-directory=$release_directory --default-repository-url=$fake_repository_url"

Initialize for the first time.

    $ $PYAM initialize

Verify.

    $ $PYAM register-new-package MyPackage --modules SiteDefs
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

    $ sandbox_directory="$CRAMTMP/example_sandbox"
    $ $PYAM setup --directory="$sandbox_directory" MyPackage

    $ $PYAM --sandbox-root-directory="$sandbox_directory" checkout SiteDefs
    $ $PYAM --sandbox-root-directory="$sandbox_directory" save SiteDefs
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)
    $ $PYAM --sandbox-root-directory="$sandbox_directory" checkout SiteDefs

When rules are not set up properly, we will get an error like
"The 'x86_64-fedora17-linux' target is not supported".
When running with "make regtest" we will get warnings like:
"make[1]: warning: jobserver unavailable: using -j1.  Add '+' to parent make rule."
However, when running with simply "srun dtest" we get nothing (no printout). We need to filter out the
warning, so we use a regex expression. However, this requires that there is a printout (even in the "srun dtest"
case). Therefore, we use an if statement to determine if this was run with "make regtest" or not, and we 
add an "echo """ accordingly.

    $ touch $sandbox_directory/src/SiteDefs/sites/site.gcc
    $ if [ -z ${MAKELEVEL+z} ]; then
    > make --quiet --directory="$sandbox_directory" all QUIET=true --no-print-directory YAM_SITE=telerobotics && echo " " && echo " " && echo " " && echo " " 
    > else
    > make --quiet --directory="$sandbox_directory" all QUIET=true --no-print-directory YAM_SITE=telerobotics
    > fi
    \s*|\s*make\[\d\]: warning: -j0 forced in submake: resetting jobserver mode\.\s* (re)
    \s*|\s*make\[\d\]: warning: -j0 forced in submake: resetting jobserver mode\.\s* (re)
    \s*|\s*make\[\d\]: warning: -j0 forced in submake: resetting jobserver mode\.\s* (re)
    \s*|\s*make\[\d\]: warning: -j0 forced in submake: resetting jobserver mode\.\s* (re)
