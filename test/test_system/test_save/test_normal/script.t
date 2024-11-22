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
    $ echo 'BRANCH_Dshell++ = Dshell++-R4-06g my_branch' >> "$CRAMTMP/FakeSandbox/YAM.config"

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

Check out branched module.

    $ pushd "$sandbox_directory" > /dev/null

    $ $PYAM rebuild 'Dshell++'
    $ popd > /dev/null

Add a good dependency file

    $ echo "abcde aD AD \n  SFSDFA mnop DSDFF" > "$sandbox_directory/src/Dshell++/bad_dep.d"

Add a bad dependency file (unmatched quotes)

    $ echo "abcde aD 'AD \n  SFSDFA\" mnop DSDFF" > "$sandbox_directory/src/Dshell++/bad_dep.d"

Check our current SVN URL.

    $ svn info "$sandbox_directory/src/Dshell++/YamVersion.h" | grep 'URL' | grep 'R4-06g' > /dev/null

Make some changes and commit them to SVN repository.

    $ pushd "$sandbox_directory/src/Dshell++" > /dev/null
    $ svn mkdir --quiet 'my_new_directory'
    $ svn commit --quiet --message 'Add directory'
    $ popd > /dev/null

--------------------------------------------------------------
Check database state before the release

    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modulePackages | grep "'Dshell++'"
    INSERT INTO `modulePackages` VALUES (62,'Dshell++',402,'MODULE',15315,15315,NULL,NULL,'FALSE','FALSE','svn');


    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modpkgReleases | grep ',62,' | grep 'R4-06'
    INSERT INTO `modpkgReleases` VALUES (14895,62,'R4-06',395,'2006-05-20 07:52:15','jain','ChangeLog, Readme, ReleaseNotes','TRUE',2,NULL,'clim-DEAD',NULL,'SOURCE',1,1,34,*,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (14945,62,'R4-06a',396,'2006-05-23 15:27:19','clim','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jmc-DEAD, jbmas',NULL,'SOURCE',0,1,34,32,25,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (14998,62,'R4-06b',397,'2006-05-31 15:34:55','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',5,NULL,'clim, jbmas',NULL,'SOURCE',1,1,34,8,39,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15123,62,'R4-06c',398,'2006-06-08 08:56:26','jain','ChangeLog, Readme, ReleaseNotes','TRUE',1,NULL,NULL,NULL,'SOURCE',1,1,34,*,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15135,62,'R4-06d',399,'2006-06-08 18:45:21','jain','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',1,1,34,*,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15173,62,'R4-06e',400,'2006-06-15 07:56:32','clim','ChangeLog, Readme, ReleaseNotes','TRUE',13,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',2,1,34,32,25,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15314,62,'R4-06f',401,'2006-07-12 08:52:57','clim','ChangeLog, Readme, ReleaseNotes','TRUE',0,NULL,'jmc-DEAD','DshellX.h','SOURCE',0,1,34,32,25,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15315,62,'R4-06g',402,'2006-07-12 14:23:04','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jbmas, jingshen, my_branch','DshellX.h','SOURCE',0,1,34,11,33,NULL,NULL,0,0,0,0,0);

--------------------------------------------------------------
Test the "save" command.

    $ pushd "$sandbox_directory" >& /dev/null
    $ EDITOR="$TESTDIR/fake-editor 'Fake message'" $PYAM_INTERACTIVE save --bug-id='' 'Dshell++'  --username $FAKE_USER
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)
    $ popd > /dev/null

Check database entry after the release. The number of releases increments, the old branch is marked dead, there is a new SOURCE release entry, the database release ids are updated

    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modulePackages | grep "'Dshell++'"
    INSERT INTO `modulePackages` VALUES (62,'Dshell++',403,'MODULE',15377,15377,NULL,NULL,'FALSE','FALSE','svn');


    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modpkgReleases | grep ',62,' | grep 'R4-06'
    INSERT INTO `modpkgReleases` VALUES (14895,62,'R4-06',395,'2006-05-20 07:52:15','jain','ChangeLog, Readme, ReleaseNotes','TRUE',2,NULL,'clim-DEAD',NULL,'SOURCE',1,1,34,*,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (14945,62,'R4-06a',396,'2006-05-23 15:27:19','clim','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jmc-DEAD, jbmas',NULL,'SOURCE',0,1,34,32,25,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (14998,62,'R4-06b',397,'2006-05-31 15:34:55','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',5,NULL,'clim, jbmas',NULL,'SOURCE',1,1,34,8,39,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15123,62,'R4-06c',398,'2006-06-08 08:56:26','jain','ChangeLog, Readme, ReleaseNotes','TRUE',1,NULL,NULL,NULL,'SOURCE',1,1,34,*,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15135,62,'R4-06d',399,'2006-06-08 18:45:21','jain','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',1,1,34,*,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15173,62,'R4-06e',400,'2006-06-15 07:56:32','clim','ChangeLog, Readme, ReleaseNotes','TRUE',13,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',2,1,34,32,25,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15314,62,'R4-06f',401,'2006-07-12 08:52:57','clim','ChangeLog, Readme, ReleaseNotes','TRUE',0,NULL,'jmc-DEAD','DshellX.h','SOURCE',0,1,34,32,25,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15315,62,'R4-06g',402,'2006-07-12 14:23:04','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jbmas, jingshen, my_branch-DEAD','DshellX.h','SOURCE',0,1,34,11,33,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15377,62,'R4-06h',403,*,'foouser','ChangeLog, ReleaseNotes','TRUE',0,NULL,NULL,'','SOURCE',0,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)


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

    $ ls -d "$sandbox_directory/src/Dshell++/my_new_directory"
    /*/FakeSandbox/src/Dshell++/my_new_directory (glob)

Make sure our release note is in there.

    $ grep 'Fake message' "$sandbox_directory/src/Dshell++/ReleaseNotes"
    \tFake message (esc)

Make sure our change log is in there.

    $ grep 'Add directory' "$sandbox_directory/src/Dshell++/ChangeLog"
    \t* Add directory (esc)

Print out the full ChangeLog entry

    $ head -10 "$sandbox_directory/src/Dshell++/ChangeLog"
    *  foouser (glob)
    
    \t* Revision tag: R4-06h (esc)
    
    \t* Add directory (esc)
    
    \t  SVN revision: 8 (esc)
    \t  A my_new_directory (esc)
    
    Wed Jul 12 14:22:11 2006\tJonathan M Cameron (jmc) (esc)







--------------------------------------------------------------
Test the "save" command - but this time with diffs disabled

Make changes to the Dshell++ module.

    $ pushd "$sandbox_directory/src/Dshell++" > /dev/null
    $ svn mkdir --quiet 'my_new_directory1'
    $ svn commit --quiet --message 'Add directory1'
    $ popd > /dev/null

    $ pushd "$sandbox_directory" >& /dev/null

    $ EDITOR="$TESTDIR/fake-editor 'Fake message1'" $PYAM_INTERACTIVE save --no-diff --bug-id='' 'Dshell++'  --username $FAKE_USER
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)
    $ popd > /dev/null

Check database entry after the release. The number of releases increments, the old branch is marked dead, there is a new SOURCE release entry, the database release ids are updated



--------------------------------------------------------------
Check out the module again.

    $ pushd "$sandbox_directory" >& /dev/null
    $ $PYAM checkout 'Dshell++'
    $ popd > /dev/null

Make sure our SVN URL is updated to be off the latest revision.

    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++/YamVersion.h"
    ^/Modules/Dshell++/featureBranches/Dshell++-R4-06i-*/YamVersion.h (glob)

Make sure the "YamVersion.h" is updated.

    $ grep 'R4-06i' "$sandbox_directory/src/Dshell++/YamVersion.h"
    #define DSHELL++_DVERSION_RELEASE "Dshell++-R4-06i"

Make sure the directory we created is still there.

    $ ls -d "$sandbox_directory/src/Dshell++/my_new_directory1"
    /*/FakeSandbox/src/Dshell++/my_new_directory1 (glob)

Make sure our release note is in there.

    $ grep 'Fake message1' "$sandbox_directory/src/Dshell++/ReleaseNotes"
    \tFake message1 (esc)

Make sure our change log is in there.

    $ grep 'Add directory1' "$sandbox_directory/src/Dshell++/ChangeLog"
    \t* Add directory1 (esc)

Print out the full ChangeLog entry

    $ head -8 "$sandbox_directory/src/Dshell++/ChangeLog"
    *  foouser (glob)
    
    \t* Revision tag: R4-06i (esc)
    
    \t* Add directory1 (esc)
    
    \t  SVN revision: 17 (esc)
    \t  A my_new_directory1 (esc)

