Test "--version".

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

    $ PYAM="$TESTDIR/../../../../pyam"

Test the command.

    $ $PYAM --version
    pyam [0-9]*\.[0-9]*.* (re)
