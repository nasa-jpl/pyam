Test "save" command.

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

Create a fake sandbox.

    $ sandbox_directory="$CRAMTMP/FakeSandbox"
    $ "$TESTDIR/../../../common/sandbox/make_fake_sandbox.bash" "$sandbox_directory"

Note that "R4-06g" is the latest.

    $ echo 'WORK_MODULES = Dshell++' >> "$CRAMTMP/FakeSandbox/YAM.config"
    $ echo 'BRANCH_Dshell++ = main' >> "$CRAMTMP/FakeSandbox/YAM.config"

Create a fake release area.

    $ release_directory="$CRAMTMP/fake_release"
    $ "$TESTDIR/../../../common/release_directory/make_fake_release_directory.bash" "$release_directory"

Start MySQL server.

    $ . "$TESTDIR/../../../common/mysql/mysql_server.bash"
    $ start_mysql_server "$TESTDIR/../../../common/mysql/example_yam_for_import.sql"
    $ PORT=$START_MYSQL_SERVER_RETURN_PORT

Create fake SVN repository.

    $ fake_repository_path="$CRAMTMP/fake_repository"
    $ "$TESTDIR/../../../common/svn/make_fake_repository.bash" "$fake_repository_path"
    $ fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"

Create an area for exporting module release ChangeLog etc links

    $ changelogs_path="$CRAMTMP/YAM_WWW"
    $ mkdir $changelogs_path

    $ PYAM="$TESTDIR/../../../../pyam --quiet --non-interactive --no-build-server --database-connection=127.0.0.1:$PORT/test --release-directory=$release_directory --default-repository-url=$fake_repository_url --changelogs-path=$changelogs_path"



---------------------------------------------------------------------------------
Check out branched module.

    $ cd "$sandbox_directory"
    $ $PYAM rebuild 'Dshell++'

Check our current revision.

    $ grep 'R4-06g' "$sandbox_directory/src/Dshell++/YamVersion.h"
    #define DSHELLPP_DVERSION_RELEASE "Dshell++-R4-06g"

Make some changes and commit them to SVN repository.

    $ cd "$sandbox_directory/src/Dshell++"
    $ svn mkdir --quiet 'my_new_directory'
    $ svn commit --quiet --message 'Add directory'

    $ ls $changelogs_path

---------------------------------------------------------------------------------
Test the "save" command.

    $ cd "$sandbox_directory"
    $ $PYAM save 'Dshell++'
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

Check out the module again.

    $ cd "$sandbox_directory"
    $ $PYAM checkout 'Dshell++'

Make sure our SVN URL is updated to be off the latest revision.

    $ svn info "$sandbox_directory/src/Dshell++/YamVersion.h" | grep 'URL' | grep 'R4-06h'
    URL: file:///*/fake_repository/Modules/Dshell++/featureBranches/Dshell++-R4-06h-*/YamVersion.h (glob)
    Relative URL: ^/Modules/Dshell++/featureBranches/Dshell++-R4-06h-*/YamVersion.h (glob)

Make sure the "YamVersion.h" is updated.

    $ grep 'R4-06h' "$sandbox_directory/src/Dshell++/YamVersion.h"
    #define DSHELL++_DVERSION_RELEASE "Dshell++-R4-06h"

Make sure the directory we created is still there.

    $ ls -d "$sandbox_directory/src/Dshell++/my_new_directory"
    /*/FakeSandbox/src/Dshell++/my_new_directory (glob)

Make sure the realease area contains the latest release

    $ ls -d "$release_directory/Module-Releases/Dshell++"
    /*/fake_release/Module-Releases/Dshell++ (glob)

Check the database entry for this release

    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modulePackages | grep "'Dshell++'"
    INSERT INTO `modulePackages` VALUES (62,'Dshell++',403,'MODULE',15377,15377,NULL,NULL,'FALSE','FALSE','svn');

    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modpkgReleases | grep ',62,' | grep "'R4-06h'"
    INSERT INTO `modpkgReleases` VALUES (15377,62,'R4-06h',403,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,'*','','SOURCE',0,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)

Verify that the links for the ChangeLog and ReleaseNotes were exported.

    $ ls -l $changelogs_path
    total 0
    *module-Dshell++-R4-06h-ChangeLog -> */fake_release/Module-Releases/Dshell++/Dshell++-R4-06h/ChangeLog (glob)
    *module-Dshell++-R4-06h-ReleaseNotes -> */fake_release/Module-Releases/Dshell++/Dshell++-R4-06h/ReleaseNotes (glob)
