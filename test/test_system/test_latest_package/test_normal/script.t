Test "latest-package" command.

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

Start MySQL server.

    $ . "$TESTDIR/../../../common/mysql/mysql_server.bash"
    $ start_read_only_mysql_server "$TESTDIR/../../../common/mysql/example_yam_for_import.sql"
    $ PORT=$READ_ONLY_MYSQL_SERVER_PORT

    $ PYAM="$TESTDIR/../../../../pyam --no-build-server --database-connection=127.0.0.1:$PORT/test"

Test the command.

    $ $PYAM latest-package
    AcsFswProtoPkg R1-01l
    AirshipPkg R1-00
    AtbeTclMesgPkg R1-05d
    CollisionDetectionPkg R1-00
    DevUtils R1-01
    Dhss R1-76d
    DhssFull R1-76b
    DmexPkg R1-14a
    DormantPkgs R1-00
    Dsends-MTP-AHEGPL-Pkg R1-01a
    DsendsMAS R1-00
    DsendsMASPkg R1-01x
    DsendsMSLPkg R1-01
    Dshdemo++FswPkg R3-35c
    Dshell++CKPkg R1-03d
    Dshell++DspacePkg R1-00a
    Dshell++DviewPkg R1-00a
    Dshell++Pkg R3-74w
    DshellDemo R1-01
    DshellDocsPkg R1-00
    DshellPkg R2-19
    DshellTutorialPkg R1-03d
    DspacePkg R1-00
    DviewNewPkg R1-05c
    DviewPkg R2-17
    EDLDshellPkg R1-05u
    ExternalDshellPkg R1-01
    FormationFlyingPkg R1-01
    FstDshellPkg R1-04
    IMDSERoverPkg R1-01
    IceDeliveryPkg R1-00
    IntegratorTestPkg R1-02
    MDSDshellPkg R1-20
    MRHESimPlatformPkg R1-00
    MslRoamsPkg R1-00
    OPSPPkg R1-01
    ObsoleteModulesPkg R1-00
    RCWRoamsPkg R1-01
    ROAMSDshellPkg R1-15s
    ROAMSMonteCarloPkg R1-00v
    RoamsFidoValidationPkg R1-00a
    RoamsSoopsPkg R1-00d
    RoamsValidationPkg R1-00c
    RocketSledPkg R1-00
    RoverDshellPkg R3-69
    RoverSlopesPkg R1-00b
    RsrDshellPkg R2-01
    SDSUDshellPkg R1-03
    ST3Pkg R1-05c
    SimPkg R2-00
    SimScapeDevPkg R1-00
    SimScapeII R1-02
    SimScapePkg R1-00a
    SimScapeSitePkg R1-00e
    SimSimPkg R1-00
    ThirdPartyPkg R1-01a
    YaMPkg R1-05b
    ds1-atbe R2-13
    lst R1-01

    $ $PYAM latest-package AcsFswProtoPkg
    AcsFswProtoPkg R1-01l

I throw out the traceback and match the actual error.

    $ $PYAM latest-package DoesNotExist |& awk '!/^Traceback|^  File|^    /'
    YaM error: Package 'DoesNotExist' does not exist

