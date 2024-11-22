Test "yamroot" script.

    $ unset YAM_ROOT
    $ YAM_ROOT_SCRIPT="$TESTDIR/../../../scripts/yamroot"

    $ mkdir 'sandbox'
    $ cd 'sandbox'
    $ $YAM_ROOT_SCRIPT
    .*[Nn]o YAM.config was found .*/sandbox (re)

    $ touch 'YAM.config'
    $ $YAM_ROOT_SCRIPT
    .*/sandbox (re)

    $ mkdir -p 'abc/def'
    $ cd 'abc/def'
    $ $YAM_ROOT_SCRIPT
    .*/sandbox (re)
