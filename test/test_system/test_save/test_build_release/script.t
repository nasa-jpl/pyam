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

    $ PYAM_NO_RELEASE_DIRECTORY="$TESTDIR/../../../../pyam --quiet --non-interactive --no-build-server --database-connection=127.0.0.1:$PORT/test --default-repository-url=$fake_repository_url"
    $ PYAM="$PYAM_NO_RELEASE_DIRECTORY --release-directory=$release_directory"

Create a fake user

    $ FAKE_USER='foouser'

Check out branched module.

    $ cd "$sandbox_directory"
    $ $PYAM rebuild 'Dshell++'

Saving with no changes and no release directory should fail.
I throw out the traceback and match the actual error.

    $ cd "$sandbox_directory"
    $ $PYAM_NO_RELEASE_DIRECTORY save 'Dshell++' |& awk '!/^Traceback|^  File|^    /'
    .* could not be saved due to the following errors.* (re)
    .* no changes.* (re)

"Build01" should not yet exist.

    $ ls "$release_directory/Module-Releases/Dshell++/Dshell++-R4-06g-Build01" >& /dev/null

Check database state before the build release

    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modulePackages | grep "'Dshell++'"
    INSERT INTO `modulePackages` VALUES (62,'Dshell++',402,'MODULE',15315,15315,NULL,NULL,'FALSE','FALSE','svn');


    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modpkgReleases | grep ',62,' | grep 'R4-06'
    INSERT INTO `modpkgReleases` VALUES (14895,62,'R4-06',395,'2006-05-20 07:52:15','jain','ChangeLog, Readme, ReleaseNotes','TRUE',2,NULL,'clim-DEAD',NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (14945,62,'R4-06a',396,'2006-05-23 15:27:19','clim','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jmc-DEAD, jbmas',NULL,'SOURCE',0,1,34,32,25,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (14998,62,'R4-06b',397,'2006-05-31 15:34:55','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',5,NULL,'clim, jbmas',NULL,'SOURCE',1,1,34,8,39,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15123,62,'R4-06c',398,'2006-06-08 08:56:26','jain','ChangeLog, Readme, ReleaseNotes','TRUE',1,NULL,NULL,NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15135,62,'R4-06d',399,'2006-06-08 18:45:21','jain','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15173,62,'R4-06e',400,'2006-06-15 07:56:32','clim','ChangeLog, Readme, ReleaseNotes','TRUE',13,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',2,1,34,32,25,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15314,62,'R4-06f',401,'2006-07-12 08:52:57','clim','ChangeLog, Readme, ReleaseNotes','TRUE',0,NULL,'jmc-DEAD','DshellX.h','SOURCE',0,1,34,32,25,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15315,62,'R4-06g',402,'2006-07-12 14:23:04','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jbmas, jingshen, my_branch','DshellX.h','SOURCE',0,1,34,11,33,NULL,NULL,0,0,0,0,0);


Save the branch with no changes.

    $ cd "$sandbox_directory"
    $ $PYAM save 'Dshell++' --username $FAKE_USER
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

"Build01" should be in the release area now.

    $ ls "$release_directory/Module-Releases/Dshell++/Dshell++-R4-06g-Build01" > /dev/null

Check database entry after the build release

    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modulePackages | grep "'Dshell++'"
    INSERT INTO `modulePackages` VALUES (62,'Dshell++',403,'MODULE',15377,15315,NULL,NULL,'FALSE','FALSE','svn');


    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modpkgReleases | grep ',62,' | grep 'R4-06'
    INSERT INTO `modpkgReleases` VALUES (14895,62,'R4-06',395,'2006-05-20 07:52:15','jain','ChangeLog, Readme, ReleaseNotes','TRUE',2,NULL,'clim-DEAD',NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (14945,62,'R4-06a',396,'2006-05-23 15:27:19','clim','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jmc-DEAD, jbmas',NULL,'SOURCE',0,1,34,32,25,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (14998,62,'R4-06b',397,'2006-05-31 15:34:55','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',5,NULL,'clim, jbmas',NULL,'SOURCE',1,1,34,8,39,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15123,62,'R4-06c',398,'2006-06-08 08:56:26','jain','ChangeLog, Readme, ReleaseNotes','TRUE',1,NULL,NULL,NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15135,62,'R4-06d',399,'2006-06-08 18:45:21','jain','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15173,62,'R4-06e',400,'2006-06-15 07:56:32','clim','ChangeLog, Readme, ReleaseNotes','TRUE',13,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',2,1,34,32,25,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15314,62,'R4-06f',401,'2006-07-12 08:52:57','clim','ChangeLog, Readme, ReleaseNotes','TRUE',0,NULL,'jmc-DEAD','DshellX.h','SOURCE',0,1,34,32,25,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15315,62,'R4-06g',402,'2006-07-12 14:23:04','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jbmas, jingshen, my_branch','DshellX.h','SOURCE',0,1,34,11,33,NULL,NULL,0,0,0,0,0);
    INSERT INTO `modpkgReleases` VALUES (15377,62,'R4-06g',403,*,'foouser','ChangeLog, ReleaseNotes','TRUE',0,'01',NULL,NULL,'BUILD',0,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)


Now we check out the Dshell++ again.

    $ cd "$sandbox_directory"
    $ $PYAM checkout 'Dshell++'

Make sure revision tag is the same since we did a build release.

    $ grep 'R4-06g' "$sandbox_directory/src/Dshell++/YamVersion.h" > /dev/null

If we remove "Build01", the next save should reuse the same build ID.

    $ rm -rf "$release_directory/Module-Releases/Dshell++/Dshell++-R4-06g-Build01"
    $ cd "$sandbox_directory"
    $ $PYAM save 'Dshell++'  --username $FAKE_USER
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)
    $ ls "$release_directory/Module-Releases/Dshell++/Dshell++-R4-06g-Build01" > /dev/null
    $ ls "$release_directory/Module-Releases/Dshell++/Dshell++-R4-06g-Build02" >& /dev/null


Test "--build-id".

    $ cd "$sandbox_directory"
    $ $PYAM checkout 'Dshell++'
    $ ls "$release_directory/Module-Releases/Dshell++/Dshell++-R4-06g-Build20131121" >& /dev/null

    $ cd "$sandbox_directory"
    $ $PYAM save --build-id=20131121 'Dshell++'  --username $FAKE_USER
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)
    $ ls "$release_directory/Module-Releases/Dshell++/Dshell++-R4-06g-Build20131121" > /dev/null
