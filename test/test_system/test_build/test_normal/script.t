Test pyam-build script.

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT
    $ export YAM_SITE="fake_site"

    $ PYAM_BUILD="$TESTDIR/../../../../pyam-build"

Start MySQL server.

    $ . "$TESTDIR/../../../common/mysql/mysql_server.bash"
    $ start_mysql_server
    $ port=$START_MYSQL_SERVER_RETURN_PORT

Create fake SVN repository.

    $ fake_repository_path="$CRAMTMP/fake_repository"
    $ svnadmin create "$fake_repository_path"
    $ fake_repository_url="file://$(readlink -f $fake_repository_path)"

Create fake configuration.

    $ release_directory="$CRAMTMP/release_directory"

    $ cat > "$CRAMTMP/test.pyamrc" << EOF
    > [pyam]
    > database-connection="127.0.0.1:$port/test"
    > default-repository-url="$fake_repository_url"
    > release-directory="$release_directory"
    > project-admin-email=arash.hosseini.jafari@jpl.nasa.gov
    > email-server=smtp.jpl.nasa.gov:25
    > email-diff-size=50000
    > site="fake_site"
    > EOF

    $ export YAM_PROJECT_CONFIG_DIR="$CRAMTMP"
    $ export YAM_PROJECT="test"

Initialize repository, database, and file system.

    $ pyam --quiet initialize

    $ ls "$release_directory"/Module-Releases/SiteDefs
    Latest
    SiteDefs-R1-00
    SiteDefs-R1-00a

Test the command.

    $ $PYAM_BUILD --quiet --pre-save-shell-command='echo hello; echo world' --modules SiteDefs FakeModule --exclude FakeModule |& grep -E  -v "Running pyam|Deleting"
    
    OBSOLETE modules= SiteDefs, FakeModule
    
    BUILD RELEASE modules= SiteDefs 
    
    
    --->  Creating sandbox directory '*/tmp*/sandbox' (glob)
    --->  Checking out sandbox metadata
      Running 'make rmlinks' subprocess: start
      Running 'make mklinks' subprocess: start
      Running 'make mklinks' subprocess: start
    --->  Created sandbox in '*/tmp*/sandbox' (glob)
    --->  Converting 'SiteDefs' to a work module
    --->  Checking out source code for 'SiteDefs' module (SiteDefs-R1-00a)
      Running 'make rmlinks' subprocess: start
      Running 'make mklinks' subprocess: start
      Running 'make mklinks' subprocess: start
      Running 'make all' subprocess: start
    hello
    world
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)
    
    These modules were saved:
    SiteDefs
    


Confirm release.

    $ ls "$release_directory"/Module-Releases/SiteDefs
    Latest
    SiteDefs-R1-00
    SiteDefs-R1-00a
    SiteDefs-R1-00a-Build01

Test with default shell command.

    $ $PYAM_BUILD --quiet --modules SiteDefs |& grep -E  -v 'Reverted|Running pyam|Deleting'
    
    OBSOLETE modules= SiteDefs
    
    BUILD RELEASE modules= SiteDefs 
    
    
    --->  Creating sandbox directory '*/tmp*/sandbox' (glob)
    --->  Checking out sandbox metadata
      Running 'make rmlinks' subprocess: start
      Running 'make mklinks' subprocess: start
      Running 'make mklinks' subprocess: start
    --->  Created sandbox in '*/tmp*/sandbox' (glob)
    --->  Converting 'SiteDefs' to a work module
    --->  Checking out source code for 'SiteDefs' module (SiteDefs-R1-00a)
      Running 'make rmlinks' subprocess: start
      Running 'make mklinks' subprocess: start
      Running 'make mklinks' subprocess: start
      Running 'make all' subprocess: start
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)
    
    These modules were saved:
    SiteDefs
    



Confirm release.

    $ ls "$release_directory"/Module-Releases/SiteDefs
    Latest
    SiteDefs-R1-00
    SiteDefs-R1-00a
    SiteDefs-R1-00a-Build01
    SiteDefs-R1-00a-Build02
