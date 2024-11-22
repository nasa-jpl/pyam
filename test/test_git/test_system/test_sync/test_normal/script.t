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
    $ echo '====== CHECKING NEW MyNewGitModule MODULE'
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

#$ echo 'Repo tags='
#$ git -C $repo_dir tag

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
    $ echo '====== CHECKING OUT MyNewGitModule-R1-00 my_branch BRANCH'
    ====== CHECKING OUT MyNewGitModule-R1-00 my_branch BRANCH

#Fill in YAM.config
    $ config_file=$sandbox_dir/YAM.config


# with open(config_file, "w" ) as config:
# 	config.write("WORK_MODULES = MyNewGitModule\n")
# 	config.write("BRANCH_MyNewGitModule = MyNewGitModule-R1-00 my_branch")

    $ $PYAM checkout MyNewGitModule --branch my_branch

    $ new_mod_dir=$sandbox_directory/src/MyNewGitModule
    $ ls $new_mod_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h

#Check out branched module
#checkout = "checkout 'MyNewGitModule'"# --repository-keyword=git"
#os.system(f'{str(pyam)} {options_str} {checkout}')

    $ git -C $new_mod_dir status -b
    On branch MyNewGitModule-R1-00-my_branch
    Your branch is up to date with 'origin/MyNewGitModule-R1-00-my_branch'.
    
    nothing to commit, working tree clean


# print('Checked out tag=')
# os.system(f'git -C {new_mod_dir} tag')
# print('Checked out branch=')
# os.system(f'git -C {new_mod_dir} branch')

#--------------------------------------------------------------------------------
	$ echo '====== MODIFYING MyNewGitModule R1-00 branch'

#add files to this branch in the sandbox

    $ cd $new_mod_dir
    $ echo "Hello There" >  $new_mod_dir/hey.txt

    $ git -C $new_mod_dir add hey.txt
    $ git -C $new_mod_dir commit -m "Added hey.txt to branch"  hey.txt
    [MyNewGitModule-R1-00-my_branch *] Added hey.txt to branch (glob)
     1 file changed, 1 insertion(+)
     create mode 100644 hey.txt

    $ git -C $new_mod_dir push
    To /tmp/cramtests-*/fake_git_repositories/Modules/MyNewGitModule (glob)
       *  MyNewGitModule-R1-00-my_branch -> MyNewGitModule-R1-00-my_branch (glob)

    $ ls $new_mod_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h
    hey.txt


#--------------------------------------------------------------------------------
    $ echo '====== SAVING MyNewGitModule R1-00 branch as R1-00a'
    ====== SAVING MyNewGitModule R1-00 branch as R1-00a

# run save command


    $ $PYAM save -m "" --bug-id='' MyNewGitModule --username='somedude'
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

    $ new_release_dir=$release_directory/Module-Releases/MyNewGitModule/MyNewGitModule-R1-00a

    $ echo 'Repo branches='
    Repo branches=
    $ git -C $repo_dir branch
      MyNewGitModule-R1-00-my_branch_dead
    * main

    $ echo 'Repo remote branches of new release='
    Repo remote branches of new release=
    $ git -C $new_release_dir branch -r
      origin/HEAD -> origin/main
      origin/MyNewGitModule-R1-00-my_branch_dead
      origin/main

	# Check tags. Should include the first two  module release.
    $ git -C $repo_dir tag
    MyNewGitModule-R1-00
    MyNewGitModule-R1-00a

    $ git -C $new_release_dir branch -l
    * (HEAD detached at MyNewGitModule-R1-00a)
      MyNewGitModule-R1-00-my_branch_dead
      main



#--------------------------------------------------------------------------------
    $ echo '====== CHECK LATEST MyNewGitModule R1-00a RELEASE'
    ====== CHECK LATEST MyNewGitModule R1-00a RELEASE


# Check the latest release value

    $ $PYAM latest 'MyNewGitModule'
    MyNewGitModule R1-00a                        -  somedude    * (glob)


    $ echo "DONE SAVING R1-00a, CHECKING OUT AGAIN"
    DONE SAVING R1-00a, CHECKING OUT AGAIN

#--------------------------------------------------------------------------------
    $ echo '====== CHECKING OUT SAVED MyNewGitModule-R1-00a my_branch BRANCH'
    ====== CHECKING OUT SAVED MyNewGitModule-R1-00a my_branch BRANCH

    $ cd $sandbox_directory
    $ $PYAM checkout MyNewGitModule --branch my_branch

    $ new_mod_dir=$sandbox_directory/src/MyNewGitModule
    $ ls $new_mod_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h
    hey.txt
 
    $ git -C $new_mod_dir status -b
    On branch MyNewGitModule-R1-00a-my_branch
    Your branch is up to date with 'origin/MyNewGitModule-R1-00a-my_branch'.
    
    nothing to commit, working tree clean


#--------------------------------------------------------------------------------
print('====== MODIFYING MyNewGitModule R1-00a branch ')

#add files to this branch in the sandbox

    $ cd $new_mod_dir
    $ echo "Hey There" >  $new_mod_dir/heythere.txt
    $ git -C $new_mod_dir add heythere.txt

    $ git -C $new_mod_dir commit -m "Added heythere.txt to branch" 
    [MyNewGitModule-R1-00a-my_branch *] Added heythere.txt to branch (glob)
     1 file changed, 1 insertion(+)
     create mode 100644 heythere.txt

    $ git -C $new_mod_dir push
    To */fake_git_repositories/Modules/MyNewGitModule (glob)
       *  MyNewGitModule-R1-00a-my_branch -> MyNewGitModule-R1-00a-my_branch (glob)

    $ git -C $new_mod_dir status
    On branch MyNewGitModule-R1-00a-my_branch
    Your branch is up to date with 'origin/MyNewGitModule-R1-00a-my_branch'.
    
    nothing to commit, working tree clean


    $ ls $new_mod_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h
    hey.txt
    heythere.txt


#--------------------------------------------------------------------------------
    $ echo '====== RE-SAVING MyNewGitModule R1-00a branch as R1-00b'
    ====== RE-SAVING MyNewGitModule R1-00a branch as R1-00b

# run save command


    $ $PYAM save -m "" --bug-id='' MyNewGitModule --username='somedude'
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)
 

    $ new_release_dir=$release_directory/Module-Releases/MyNewGitModule/MyNewGitModule-R1-00b

    $ echo 'Repo branches='
    Repo branches=
    $ git -C $repo_dir branch
      MyNewGitModule-R1-00-my_branch_dead
      MyNewGitModule-R1-00a-my_branch_dead
    * main

    $ echo 'Repo remote branches of new release='
    Repo remote branches of new release=
    $ git -C $new_release_dir branch -r
      origin/HEAD -> origin/main
      origin/MyNewGitModule-R1-00-my_branch_dead
      origin/MyNewGitModule-R1-00a-my_branch_dead
      origin/main

	# Check tags. Should include the first three module release.
    $ git -C $repo_dir tag
    MyNewGitModule-R1-00
    MyNewGitModule-R1-00a
    MyNewGitModule-R1-00b

    $ git -C $new_release_dir branch -l
    * (HEAD detached at MyNewGitModule-R1-00b)
      MyNewGitModule-R1-00a-my_branch_dead
      main

#--------------------------------------------------------------------------------
    $ echo '====== CHECK LATEST MyNewGitModule R1-00b RELEASE'
    ====== CHECK LATEST MyNewGitModule R1-00b RELEASE

# Check the latest release value

    $ $PYAM latest 'MyNewGitModule'
    MyNewGitModule R1-00b                        -  somedude    * (glob)

#--------------------------------------------------------------------------------
    $ echo '====== CHECKING OUT NEW MyNewGitModule-R1-00a branch module'
    ====== CHECKING OUT NEW MyNewGitModule-R1-00a branch module

 

    $ cd $sandbox_directory
    $ $PYAM scrap MyNewGitModule --remove
    $ $PYAM checkout MyNewGitModule --release R1-00a --branch my_branch2

    $ new_mod_dir=$sandbox_directory/src/MyNewGitModule
    $ ls $new_mod_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h
    hey.txt
 
    $ git -C $new_mod_dir status -b
    On branch MyNewGitModule-R1-00a-my_branch2
    Your branch is up to date with 'origin/MyNewGitModule-R1-00a-my_branch2'.
    
    nothing to commit, working tree clean

#--------------------------------------------------------------------------------
print('====== MODIFYING MyNewGitModule new R1-00a branch ')

#add files to this branch in the sandbox

    $ cd $new_mod_dir
    $ echo "Hey There2" >  $new_mod_dir/heythere2.txt
    $ git -C $new_mod_dir add heythere2.txt

    $ git -C $new_mod_dir commit -m "Added heythere2.txt to branch" 
    [MyNewGitModule-R1-00a-my_branch2 *] Added heythere2.txt to branch (glob)
     1 file changed, 1 insertion(+)
     create mode 100644 heythere2.txt

    $ git -C $new_mod_dir push
    To */fake_git_repositories/Modules/MyNewGitModule (glob)
       *  MyNewGitModule-R1-00a-my_branch2 -> MyNewGitModule-R1-00a-my_branch2 (glob)

    $ git -C $new_mod_dir status
    On branch MyNewGitModule-R1-00a-my_branch2
    Your branch is up to date with 'origin/MyNewGitModule-R1-00a-my_branch2'.
    
    nothing to commit, working tree clean


    $ ls $new_mod_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h
    hey.txt
    heythere2.txt


#--------------------------------------------------------------------------------
    $ echo '====== SYNC MyNewGitModule new R1-00a branch to R1-00b branch'
    ====== SYNC MyNewGitModule new R1-00a branch to R1-00b branch


# run save command


    $ $PYAM sync MyNewGitModule
    Syncing MyNewGitModule work module to its latest release


    $ echo 'Repo branches='
    Repo branches=
    $ git -C $repo_dir branch
      MyNewGitModule-R1-00-my_branch_dead
      MyNewGitModule-R1-00a-my_branch2_dead
      MyNewGitModule-R1-00a-my_branch_dead
      MyNewGitModule-R1-00b-my_branch2
    * main

    $ echo 'Repo remote branches='
    Repo remote branches=
    $ git -C $repo_dir branch -r

	# Check tags. Should include the first three module release.
    $ git -C $repo_dir tag
    MyNewGitModule-R1-00
    MyNewGitModule-R1-00a
    MyNewGitModule-R1-00b

    $ git -C $new_mod_dir status
    On branch MyNewGitModule-R1-00b-my_branch2
    Your branch is up to date with 'origin/MyNewGitModule-R1-00b-my_branch2'.
    
    All conflicts fixed but you are still merging.
      (use "git commit" to conclude merge)
    
    Changes to be committed:
    \tnew file:   heythere2.txt (esc)
    


    $ ls $new_mod_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h
    hey.txt
    heythere.txt
    heythere2.txt


