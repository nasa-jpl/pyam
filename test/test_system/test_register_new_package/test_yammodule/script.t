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

    $ echo "MODULES_MyNewPkg = SiteDefs Dshell++ SimScape" >> "$CRAMTMP/junk/YAM.modules"
    $ svn commit -m "Added MyNewPkg definition" "$CRAMTMP/junk/YAM.modules"
    Sending        junk/YAM.modules
    Transmitting file data .done
    Committing transaction...
    Committed revision 30.


Test "register-new-package".

    $ $PYAM register-new-package MyNewPkg
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

Verify by checking out the package as a sandbox.

    $ sandbox_directory="$CRAMTMP/example_sandbox"
    $ $PYAM setup --directory="$sandbox_directory" MyNewPkg

    $ ls -d "$sandbox_directory"
    */example_sandbox (glob)
    $ ls -d "$sandbox_directory/YAM.config"
    */example_sandbox/YAM.config (glob)
    $ ls -d "$sandbox_directory/Makefile"
    */example_sandbox/Makefile (glob)
    $ ls -d "$sandbox_directory/common"
    */example_sandbox/common (glob)

Check that the sandbox directory is checked out from "Packages/.../trunk"

    $ svn info --show-item relative-url "$sandbox_directory"
    ^/Packages/MyNewPkg/trunk


Check that the sandbox directory is checked out from "common/trunk"

    $ svn info --show-item relative-url "$sandbox_directory/common"
    ^/common/trunk



Verify that the new package definition has been added to common/YAM.module contents

    $ grep 'MODULES_' "$sandbox_directory/common/YAM.modules"
    # Variables of the form MODULES_pkg should be set in this file, where "pkg" is
    # file to specify a variable of the form "MODULES_bar = foo baz"
    # $(MODULES_pkg2) in its list of modules, where "pkg2" is the name of the other
    MODULES_MyNewPkg = SiteDefs Dshell++ SimScape

Verify that the latest release of the new package is R1-00

    $ $PYAM latest-package
    MyNewPkg R1-00


Verifying by checking out a tagged package.

    $ rm -rf "$sandbox_directory"
    $ $PYAM setup --directory="$sandbox_directory" --revision-tag='R1-00' MyNewPkg

    $ ls -d "$sandbox_directory"
    */example_sandbox (glob)
    $ ls -d "$sandbox_directory/YAM.config"
    */example_sandbox/YAM.config (glob)
    $ ls -d "$sandbox_directory/Makefile"
    */example_sandbox/Makefile (glob)
    $ ls -d "$sandbox_directory/common"
    */example_sandbox/common (glob)

Check that the sandbox directory is checked out from "Packages/.../releases"

    $ svn info --show-item relative-url "$sandbox_directory"
    ^/Packages/MyNewPkg/releases/MyNewPkg-R1-00


Check that the sandbox directory is checked out from "Packages/.../releases/.../common"

    $ svn info --show-item relative-url "$sandbox_directory/common"
    ^/Packages/MyNewPkg/releases/MyNewPkg-R1-00/common
