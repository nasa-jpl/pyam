Test "obsolete-builds" command.

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

    $ PYAM="$TESTDIR/../../../../pyam --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --no-build-server --database-connection=127.0.0.1:$PORT/test"

Print the names of the modules whose builds are obsolete.

    $ $PYAM obsolete-builds | sort
    ACSModels
    ANN
    AcmeModels
    AmesMSF_IF
    AnnModels
    AtbeTclMesg
    CVode
    CameraImageModels
    CameraResponse
    ContactModels
    Craft
    DSolverModels
    Darts
    DartsExtIK
    DefunctModels
    Dhss
    DhssModels
    Dmex
    DmexStubModels
    Dnoise
    DshellDspace
    DshellEnvCache
    DshellEnvClient
    DshellExpr
    DshellScope
    DshellSwift
    Dshtcl++
    DspaceTerrain
    EDLAeroModels
    EnvClient
    EnvClientTest
    EphemPropagatorModels
    FSTModels
    FidoValidation
    GeneralModels
    Gestalt
    GllModels
    GravityModels
    IKGraph
    IntegratorModels
    IntegratorTest
    Ksolv
    LaRCModels
    MDSModels
    MachineVisionCore
    MarsGRAM2005Models
    MathTclUtils
    MatlabServer
    MpfModels
    MslModels
    NrovModels
    OPSPModels
    RoamsDev
    RoverDynModels
    RoverModels
    RoverNavModels
    RoverTests
    RsrAcsModels
    RsrModels
    SOA
    SimModels
    SimScape
    SimScape-Import
    SimScape-VisSite
    SimScapeMigration
    SimScapeVista
    SiteEnvClient
    SiteEnvClientTest
    Spice
    SpiceModels
    SpicePositionModels
    StarlightModels
    SurfaceContact
    SwigTclDot
    TerrainInstrumentServer
    TerrainObject
    TerrainSurface
    Vista
    aejModels
    gusto
    libMSIM
    spk2darts
