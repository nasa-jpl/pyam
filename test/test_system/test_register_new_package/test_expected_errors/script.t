Test registering of a new package, where the package definition is
already present in the YAM.modules file.

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

Start empty MySQL server.

    $ . "$TESTDIR/../../../common/mysql/mysql_server.bash"
    $ start_mysql_server '/dev/null'
    $ PORT=$START_MYSQL_SERVER_RETURN_PORT

Initialize pyam.

    $ release_directory="$CRAMTMP/fake_release"
    $ fake_repository_path="$CRAMTMP/fake_repository"
    $ svnadmin create "$fake_repository_path"
    $ fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"

    $ PYAM="$TESTDIR/../../../../pyam --quiet --non-interactive --no-build-server --database-connection=127.0.0.1:$PORT/test --release-directory=$release_directory --default-repository-url=$fake_repository_url --site=telerobotics"

    $ $PYAM initialize
    $ $PYAM register-new-module Dshell++
    $ $PYAM register-new-module SimScape

Check that there are no packages registered at this point

    $ $PYAM latest-package

Verify that the new package definition is not currently in common/YAM.modules in the repository

    $ svn checkout "$fake_repository_url/common/trunk"  "$CRAMTMP/junk"
    A    */junk/Makefile (glob)
    A    */junk/README (glob)
    A    */junk/YAM.modules (glob)
    Checked out revision 29.


    $ grep 'MODULES_' "$CRAMTMP/junk/YAM.modules"
    # Variables of the form MODULES_pkg should be set in this file, where "pkg" is
    # file to specify a variable of the form "MODULES_bar = foo baz"
    # $(MODULES_pkg2) in its list of modules, where "pkg2" is the name of the other

    $ echo "MODULES_MyNewPkg = SiteDefs Dshell++" >> "$CRAMTMP/junk/YAM.modules"
    $ svn commit -m "Added MyNewPkg definition" "$CRAMTMP/junk/YAM.modules"
    Sending        junk/YAM.modules
    Transmitting file data .done
    Committing transaction...
    Committed revision 30.


Test "register-new-package" - should fail because of mismatch in package definitions

    $ $PYAM register-new-package MyNewPkg --modules Dshell++ SimScape  |& awk '!/^Traceback|^  File|^    /'
    ValueError: The command line modules list ['SiteDefs', 'Dshell++', 'SimScape'] does not match the ['Dshell++', 'SiteDefs'] modules list in YAM.modules for the MyNewPkg package.


Test "register-new-package" with empty package definition - should fail


  ######$ $PYAM register-new-package EmptyNewPkg  |& awk '!/^Traceback|^  File|^    /'



    $ $PYAM register-new-package EmptyNewPkg  |& awk '/^ValueError: Need to specify the modules list/'
    ValueError: Need to specify the modules list for the new EmptyNewPkg package either on the command line or in YAM.modules.
