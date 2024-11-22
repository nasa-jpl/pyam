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

Set command-line parameters.

    $ PYAM="$TESTDIR/../../../../../pyam --quiet --release-directory=$release_directory --no-build-server --database-connection=127.0.0.1:$port/test --default-repository-url=$fake_svn_repository_url"


    $ git_remotes=$CRAMTMP/fake_git_repositories/Modules
    $ module_repos_folder=$git_remotes

    $ cd "$sandbox_directory"
#--------------------------------------------------------------



#--------------------------------------------------------------------------------
    $ echo '====== CREATING NEW MyNewGitModule MODULE '
    ====== CREATING NEW MyNewGitModule MODULE 

#Run the register-new-module-command


    $ ls $module_repos_folder
    MyNewGitModule

    $ $PYAM --keyword-to-repository-url=git=$git_remotes  register-new-module MyNewGitModuleAlt --repository-keyword=git


    $ new_release_dir=$release_directory/Module-Releases/MyNewGitModuleAlt/MyNewGitModuleAlt-R1-00

#check that above command created release directory

    $ ls $new_release_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h

#it should also have made the repo in the remotes folder

    $ repo_dir=$module_repos_folder/MyNewGitModuleAlt

    $ ls $module_repos_folder
    MyNewGitModule
    MyNewGitModuleAlt

#    $ ls $repo_dir    
#    ChangeLog
#    Makefile
#    Makefile.yam
#    ReleaseNotes
#    YamVersion.h

$ echo 'Repo tags='
$ git -C $repo_dir tag

	# Check Repo branches. Should only include main.
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
    MyNewGitModuleAlt-R1-00

#$ echo 'Release tags in release dir='
#$ git -C $new_release_dir tag

#$ echo 'Branch in release dir (should be release tag)'
#$ git -C $new_release_dir describe --tags

    $ git -C $new_release_dir branch -l
    * (HEAD detached at MyNewGitModuleAlt-R1-00)
      main

    $ git -C $new_release_dir status -b
    HEAD detached at MyNewGitModuleAlt-R1-00
    nothing to commit, working tree clean

####$ git -C $new_release_dir status

    $ echo "Register New Module Command Done"
    Register New Module Command Done

#--------------------------------------------------------------------------------
    $ echo '====== CHECK LATEST MyNewGitModuleAlt RELEASE'
    ====== CHECK LATEST MyNewGitModuleAlt RELEASE

# Check the latest release value

    $ $PYAM latest MyNewGitModuleAlt  MyNewGitModule Dshell++
    MyNewGitModuleAlt R1-00                      -  -         * (glob)
    MyNewGitModule R1-00                         -  -           2022-06-05 18:47:41
    Dshell++ R4-06g                              -  jmc         2006-07-12 14:23:04
 

