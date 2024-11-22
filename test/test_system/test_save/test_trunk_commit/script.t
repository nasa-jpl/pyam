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
    $ echo 'BRANCH_Dshell++ = main'  >> "$CRAMTMP/FakeSandbox/YAM.config"

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

    $ PYAM_INTERACTIVE="$TESTDIR/../../../../pyam --quiet --require-bug-id --no-build-server --database-connection=127.0.0.1:$PORT/test --release-directory=$release_directory --default-repository-url=$fake_repository_url"
    $ PYAM="$PYAM_INTERACTIVE --non-interactive"

Create a fake user

    $ FAKE_USER='foouser'



-------------------------------------
Check out trunk  module.

    $ pushd "$sandbox_directory" > /dev/null

    $ $PYAM rebuild 'Dshell++'
    $ popd > /dev/null

Check our current SVN URL.

    $ svn info --show-item relative-url  "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/trunk

Make some changes and commit them to trunk.

    $ pushd "$sandbox_directory/src/Dshell++" > /dev/null
    $ svn mkdir --quiet 'my_trunk_directory'
    $ svn commit --quiet --message 'Add main trunk directory'
    $ popd > /dev/null

---------------------------------------
Check out branch  module.

    $ pushd "$sandbox_directory" > /dev/null
    $ $PYAM scrap --remove Dshell++
    $ $PYAM checkout 'Dshell++' --branch fake
    $ popd > /dev/null

Check our current SVN URL.

    $ svn info --show-item relative-url  "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/featureBranches/Dshell++-R4-06g-fake

Make some changes and commit them to the branch.

    $ pushd "$sandbox_directory/src/Dshell++" > /dev/null
    $ svn mkdir --quiet 'my_branch_directory'
    $ svn commit --quiet --message 'Add branch directory'
    $ svn mkdir --quiet 'my_branch_sec_directory'
    $ svn commit --quiet --message 'Add second branch directory'
    $ popd > /dev/null



--------------------------------------------------------------
Test the "save" command.

    $ pushd "$sandbox_directory" >& /dev/null
    $ EDITOR="$TESTDIR/fake-editor 'Fake message'" $PYAM_INTERACTIVE save --bug-id='' 'Dshell++'  --username $FAKE_USER
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)
    $ popd > /dev/null

Check database entry after the release. The number of releases increments, the old branch is marked dead, there is a new SOURCE release entry, the database release ids are updated

    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modulePackages | grep "'Dshell++'"
    INSERT INTO `modulePackages` VALUES (62,'Dshell++',403,'MODULE',15377,15377,NULL,NULL,'FALSE','FALSE','svn');



--------------------------------------------------------------
Check out the module again.

    $ pushd "$sandbox_directory" >& /dev/null
    $ $PYAM checkout 'Dshell++'
    $ popd > /dev/null

Make sure our SVN URL is updated to be off the latest revision.

    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++/YamVersion.h"
    ^/Modules/Dshell++/featureBranches/Dshell++-R4-06h-*/YamVersion.h (glob)

Make sure the "YamVersion.h" is updated.

    $ grep 'R4-06h' "$sandbox_directory/src/Dshell++/YamVersion.h"
    #define DSHELL++_DVERSION_RELEASE "Dshell++-R4-06h"

Make sure the directory we created is still there.

    $ ls -d "$sandbox_directory/src/Dshell++/my_trunk_directory"
    /*/FakeSandbox/src/Dshell++/my_trunk_directory (glob)

    $ ls -d "$sandbox_directory/src/Dshell++/my_branch_directory"
    /*/FakeSandbox/src/Dshell++/my_branch_directory (glob)

Make sure our release note is in there.

    $ grep 'Fake message' "$sandbox_directory/src/Dshell++/ReleaseNotes"
    \tFake message (esc)

Print out the full ChangeLog entry and verify that both main trunk and
branch commit messages are present.

    $ head -20 "$sandbox_directory/src/Dshell++/ChangeLog"
    *  foouser (glob)
    
    \t* Revision tag: R4-06h (esc)
    
    \t* Add second branch directory (esc)
    
    \t  SVN revision: 10 (esc)
    \t  A my_branch_sec_directory (esc)
    
    \t* Add branch directory (esc)
    
    \t  SVN revision: 9 (esc)
    \t  A my_branch_directory (esc)
    
    \t* Add main trunk directory (esc)
    
    \t  SVN revision: 7 (esc)
    \t  A my_trunk_directory (esc)
    
    Wed Jul 12 14:22:11 2006\tJonathan M Cameron (jmc) (esc)
