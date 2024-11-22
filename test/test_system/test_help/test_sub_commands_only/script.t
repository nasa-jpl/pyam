Test "latest" command.

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

    $ PYAM="$TESTDIR/../../../../pyam --no-build-server --database-connection=127.0.0.1:12345/fake"

Test the command.

    $ $PYAM help | tr '\n' ' '
    .* positional .* (re)

    $ $PYAM latest --help | tr '\n' ' '
    usage: pyam latest .* (re)
