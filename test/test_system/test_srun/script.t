Test "yamroot" script.

    $ unset YAM_ROOT
    $ SRUN_SCRIPT="$TESTDIR/../../../scripts/srun"

    $ mkdir 'sandbox'
    $ cd 'sandbox'
    $ $SRUN_SCRIPT "$TESTDIR/echo_yam_root.bash"
    srun must be run from within a sandbox

    $ touch 'YAM.config'
    $ mkdir 'bin'
    $ cat > 'bin/Drun' << EOF
    > #!/bin/bash
    > echo 'Drun ran'
    > EOF
    $ chmod +x 'bin/Drun'

    $ $SRUN_SCRIPT
    Drun ran
