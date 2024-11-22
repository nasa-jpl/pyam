Test "checkout" command.

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

$ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

Set up.

    $ fakedatatar=$TESTDIR/../../../../common/pyamfakedata.tar.gz
    $ tar zxf $fakedatatar  -C $CRAMTMP
    $ mv  $CRAMTMP/pyamfakedata/*  $CRAMTMP

    $ sandbox_directory="$CRAMTMP/FakeSandbox"


    $ release_directory="$CRAMTMP/fake_release"


Start MySQL server.

    $ . "$TESTDIR/../../../../common/mysql/mysql_server.bash"
    $ start_mysql_server "$TESTDIR/../../../../common/mysql/example_yam_for_import.sql"
    $ port=$START_MYSQL_SERVER_RETURN_PORT

Create fake SVN repository.

    $ fake_svn_repository_path="$CRAMTMP/fake_svn_repository"


    $ fake_svn_repository_url="file://`readlink -f \"$fake_svn_repository_path\"`"
    $ git_remotes=$CRAMTMP/fake_git_repositories/Modules

Set command-line parameters.

    $ PYAM="$TESTDIR/../../../../../pyam --quiet --release-directory=$release_directory --no-build-server --database-connection=127.0.0.1:$port/test --default-repository-url=$fake_svn_repository_url --keyword-to-repository-url=git=$git_remotes"


    $ module_repos_folder=$git_remotes

    $ cd "$sandbox_directory"
#--------------------------------------------------------------



#--------------------------------------------------------------------------------
    $ echo '====== CHECKING NEW MyNewGitModule MODULE '
    ====== CHECKING NEW MyNewGitModule MODULE 


#Run the register-new-module-command


# not needed any more. Initial release already exists
###    $ $PYAM register-new-module MyNewGitModule --repository-keyword=git


    $ new_release_dir=$release_directory/Module-Releases/MyNewGitModule/MyNewGitModule-R1-00

#check that above command created release directory

    $ ls $new_release_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h

#it should also have made the repo in the remotes folder

    $ repo_dir=$module_repos_folder/MyNewGitModule

#    $ ls $repo_dir
#    ChangeLog
#    Makefile
#    Makefile.yam
#    ReleaseNotes
#    YamVersion.h

$ echo 'Repo tags='
$ git -C $repo_dir tag

    $ echo 'Repo branches='
    Repo branches=
    $ git -C $repo_dir branch
    * main

	# Check remote branches. Should be none since this is the main, bare repository.
    $ echo 'Repo remote branches='
    Repo remote branches=
    $ git -C $repo_dir branch -r

	# Check tags. Should only include the first module release.
    $ git -C $repo_dir tag
    MyNewGitModule-R1-00

#$ echo 'Release tags in release dir='
#$ git -C $new_release_dir tag

#$ echo 'Branch in release dir (should be release tag)'
#$ git -C $new_release_dir describe --tags

    $ git -C $new_release_dir branch -l
    * (HEAD detached at MyNewGitModule-R1-00)
      main

    $ git -C $new_release_dir status -b
    HEAD detached at MyNewGitModule-R1-00
    nothing to commit, working tree clean

####$ git -C $new_release_dir status

    $ echo "Register New Module Command Done"
    Register New Module Command Done

#--------------------------------------------------------------------------------
    $ echo '====== CHECK LATEST MyNewGitModule RELEASE'
    ====== CHECK LATEST MyNewGitModule RELEASE

# Check the latest release value

    $ $PYAM latest 'MyNewGitModule'  Dshell++
    MyNewGitModule R1-00                         -  -           * (glob)
    Dshell++ R4-06g                              -  jmc         2006-07-12 14:23:04


#--------------------------------------------------------------------------------
    $ echo '====== CHECKING OUT MyNewGitModule-R1-00 trunk'
    ====== CHECKING OUT MyNewGitModule-R1-00 trunk

#Fill in YAM.config
    $ config_file=$sandbox_dir/YAM.config



    $ $PYAM checkout MyNewGitModule --release main

    $ new_mod_dir=$sandbox_directory/src/MyNewGitModule
    $ ls $new_mod_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h

    $ git -C $new_mod_dir status -b
    On branch main
    Your branch is up to date with 'origin/main'.
    
    nothing to commit, working tree clean

