Test registering of a new package.

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

    $ PYAM="$TESTDIR/../../../../pyam --quiet --non-interactive --no-build-server --database-connection=127.0.0.1:$PORT/test --release-directory=$release_directory --default-repository-url=$fake_repository_url"

    $ $PYAM initialize
    $ $PYAM register-new-module Dshell++
    $ $PYAM register-new-module SimScape

-----------------------------------------------------------------------------
Create a new package.

    $ $PYAM register-new-package MyNewPkg --modules Dshell++ SimScape
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

-----------------------------------------------------------------------------
Test "save-package"

    $ $PYAM save-package --revision-tag='R9-99z' MyNewPkg
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

Verifying by checking out a tagged package.

    $ sandbox_directory="$CRAMTMP/sandbox"
    $ $PYAM setup --revision-tag='R9-99z' --directory="$sandbox_directory" MyNewPkg

    $ ls -d "$sandbox_directory"
    */sandbox (glob)

    $ grep 'SimScape' "$sandbox_directory/YAM.config"
                   SimScape/SimScape-R1-00 \
    # BRANCH_SimScape = SimScape-R1-00  * (glob)

    $ ls -d "$sandbox_directory/Makefile"
    */sandbox/Makefile (glob)

    $ ls -d "$sandbox_directory/common"
    */sandbox/common (glob)

Check that the sandbox directory is checked out from "Packages/.../releases"

    $ svn info --show-item relative-url $sandbox_directory
    ^/Packages/MyNewPkg/releases/MyNewPkg-R9-99z

Check that the sandbox directory is checked out from "Packages/.../releases/.../common"

    $ svn info --show-item relative-url "$sandbox_directory/common"
    ^/Packages/MyNewPkg/releases/MyNewPkg-R9-99z/common


    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modulePackages | grep 'MyNewPkg'
    INSERT INTO `modulePackages` VALUES (427,'MyNewPkg',2,'PACKAGE',18453,18453,NULL,NULL,'FALSE','FALSE','svn');

    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modpkgReleases | grep ',427,'
    INSERT INTO `modpkgReleases` VALUES (18452,427,'R1-00',1,'*','*',NULL,'TRUE',3,NULL,NULL,NULL,'PACKAGE',0,1,1,1,1,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (18453,427,'R9-99z',2,'*','*',NULL,'TRUE',3,NULL,NULL,NULL,'PACKAGE',0,1,1,1,1,NULL,NULL,0,0,0,0,0); (glob)
