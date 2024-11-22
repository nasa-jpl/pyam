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


    $ R1_00_release_dir=$release_directory/Module-Releases/MyNewGitModule/MyNewGitModule-R1-00

#check that above command created release directory

    $ ls $R1_00_release_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h

    $ git -P -C $R1_00_release_dir status -b
    HEAD detached at MyNewGitModule-R1-00
    nothing to commit, working tree clean

#it should also have made the repo in the remotes folder

    $ repo_dir=$module_repos_folder/MyNewGitModule

#    $ ls $repo_dir
#    ChangeLog
#    Makefile
#    Makefile.yam
#    ReleaseNotes
#    YamVersion.h

#$ echo 'Repo tags='
#$ git -P -C $repo_dir tag

    $ echo 'Repo branches='
    Repo branches=
    $ git -P -C $repo_dir branch
    * main

	# Check remote branches. Should be none since this is the main, bare repository.
    $ echo 'Repo remote branches='
    Repo remote branches=
    $ git -C $repo_dir branch -r

	# Check tags. Should only include the first module release.
    $ git -C $repo_dir tag
    MyNewGitModule-R1-00

#$ echo 'Release tags in release dir='
#$ git -P -C $R1_00_release_dir tag

#$ echo 'Branch in release dir (should be release tag)'
#$ git -P -C $R1_00_release_dir describe --tags

    $ git -P -C $R1_00_release_dir branch -l
    * (HEAD detached at MyNewGitModule-R1-00)
      main

    $ git -P -C $R1_00_release_dir status -b
    HEAD detached at MyNewGitModule-R1-00
    nothing to commit, working tree clean

####$ git -P -C $R1_00_release_dir status

    $ echo "Register New Module Command Done"
    Register New Module Command Done

    $ cat $R1_00_release_dir/ChangeLog
    
    $ grep 'define MYNEWGITMODULE_DVERSION_RELEASE' $R1_00_release_dir/YamVersion.h


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

    $ sbox_mod_dir=$sandbox_directory/src/MyNewGitModule
    $ ls $sbox_mod_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h

#Check out branched module
#checkout = "checkout 'MyNewGitModule'"# --repository-keyword=git"
#os.system(f'{str(pyam)} {options_str} {checkout}')

    $ git -P -C $sbox_mod_dir status -b
    On branch MyNewGitModule-R1-00-my_branch
    Your branch is up to date with 'origin/MyNewGitModule-R1-00-my_branch'.
    
    nothing to commit, working tree clean


# print('Checked out tag=')
# os.system(f'git -P -C {sbox_mod_dir} tag')
# print('Checked out branch=')
# os.system(f'git -P -C {sbox_mod_dir} branch')

#--------------------------------------------------------------------------------
	$ echo '====== MODIFYING MyNewGitModule R1-00a branch'

#add files to this branch in the sandbox

    $ cd $sbox_mod_dir
    $ echo "Hello There" >  $sbox_mod_dir/hey.txt

    $ git -P -C $sbox_mod_dir add hey.txt
    $ git -P -C $sbox_mod_dir commit -m "Added hey.txt to branch"  hey.txt
    [MyNewGitModule-R1-00-my_branch *] Added hey.txt to branch (glob)
     1 file changed, 1 insertion(+)
     create mode 100644 hey.txt

    $ git -P -C $sbox_mod_dir push
    To */fake_git_repositories/Modules/MyNewGitModule (glob)
       *  MyNewGitModule-R1-00-my_branch -> MyNewGitModule-R1-00-my_branch (glob)

    $ ls $sbox_mod_dir
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

    $ R1_00a_release_dir=$release_directory/Module-Releases/MyNewGitModule/MyNewGitModule-R1-00a

    $ ls $R1_00a_release_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h
    hey.txt
 
#    $ ls $repo_dir
#    ChangeLog
#    Makefile
#    Makefile.yam
#    ReleaseNotes
#    YamVersion.h
#    hey.txt
 
    $ git -P -C $R1_00a_release_dir status -b
    HEAD detached at MyNewGitModule-R1-00a
    nothing to commit, working tree clean

    $ echo 'Repo branches='
    Repo branches=
    $ git -P -C $repo_dir branch
      MyNewGitModule-R1-00-my_branch_dead
    * main

    $ echo 'Repo remote branches of R1-00a release='
    Repo remote branches of R1-00a release=
    $ git -C $R1_00a_release_dir branch -r
      origin/HEAD -> origin/main
      origin/MyNewGitModule-R1-00-my_branch_dead
      origin/main

	# Check tags. Should include the first two module release.
    $ git -C $repo_dir tag
    MyNewGitModule-R1-00
    MyNewGitModule-R1-00a

    $ git -P -C $R1_00a_release_dir branch -l
    * (HEAD detached at MyNewGitModule-R1-00a)
      MyNewGitModule-R1-00-my_branch_dead
      main

    $ cat $R1_00a_release_dir/ChangeLog
    *  somedude (glob)
    
    \t* Revision tag: R1-00a (esc)
    
    \tcommit * (esc) (glob)
    \tAuthor: * (esc) (glob)
    \tDate:   * (esc) (glob)
    
    \t    Added hey.txt to branch (esc)
    
    


    $ grep 'define MYNEWGITMODULE_DVERSION_RELEASE' $R1_00a_release_dir/YamVersion.h
    #define MYNEWGITMODULE_DVERSION_RELEASE "MyNewGitModule-R1-00a"



#--------------------------------------------------------------------------------
    $ echo '====== CHECK LATEST MyNewGitModule R1-00a RELEASE'
    ====== CHECK LATEST MyNewGitModule R1-00a RELEASE


# Check the latest release value

    $ $PYAM latest 'MyNewGitModule'
    MyNewGitModule R1-00a                        -  somedude    * (glob)


    $ echo "DONE SAVING R1-00a, CHECKING OUT AGAIN"
    DONE SAVING R1-00a, CHECKING OUT AGAIN

#--------------------------------------------------------------------------------
    $ echo '====== CHECKING OUT SAVED MyNewGitModule-R1-00a MAIN version'
    ====== CHECKING OUT SAVED MyNewGitModule-R1-00a MAIN version

    $ cd $sandbox_directory
    $ $PYAM checkout MyNewGitModule --release main

    $ ls $sbox_mod_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h
    hey.txt
 
    $ git -P -C $sbox_mod_dir status -b
    On branch main
    Your branch is up to date with 'origin/main'.
    
    nothing to commit, working tree clean


#--------------------------------------------------------------------------------
    $ echo '====== CHECKING OUT SAVED MyNewGitModule-R1-00a tagged'
    ====== CHECKING OUT SAVED MyNewGitModule-R1-00a tagged

    $ cd $sandbox_directory
    $ $PYAM scrap --remove MyNewGitModule
    $ $PYAM checkout MyNewGitModule --branch -

    $ ls $sbox_mod_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h
    hey.txt
 
    $ git -P -C $sbox_mod_dir status -b
    HEAD detached at MyNewGitModule-R1-00a
    nothing to commit, working tree clean


#--------------------------------------------------------------------------------
    $ echo '====== CHECKING OUT SAVED MyNewGitModule-R1-00a my_branch BRANCH'
    ====== CHECKING OUT SAVED MyNewGitModule-R1-00a my_branch BRANCH

    $ cd $sandbox_directory
    $ $PYAM scrap --remove MyNewGitModule
    $ $PYAM checkout MyNewGitModule --branch my_branch

    $ ls $sbox_mod_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h
    hey.txt
 
    $ git -P -C $sbox_mod_dir status -b
    On branch MyNewGitModule-R1-00a-my_branch
    Your branch is up to date with 'origin/MyNewGitModule-R1-00a-my_branch'.
    
    nothing to commit, working tree clean


#--------------------------------------------------------------------------------
print('====== MODIFYING MyNewGitModule R1-00a branch ')

#add files to this branch in the sandbox

    $ cd $sbox_mod_dir
    $ echo "Hey There" >  $sbox_mod_dir/heythere.txt
    $ echo "Hey Line 2" >  $sbox_mod_dir/hey.txt
    $ git -P -C $sbox_mod_dir add heythere.txt hey.txt

    $ git -P -C $sbox_mod_dir commit -m "Added heythere.txt to branch" 
    [MyNewGitModule-R1-00a-my_branch *] Added heythere.txt to branch (glob)
     2 files changed, 2 insertions(+), 1 deletion(-)
     create mode 100644 heythere.txt

    $ git -P -C $sbox_mod_dir push
    To */fake_git_repositories/Modules/MyNewGitModule (glob)
       *  MyNewGitModule-R1-00a-my_branch -> MyNewGitModule-R1-00a-my_branch (glob)




    $ git -P -C $sbox_mod_dir status
    On branch MyNewGitModule-R1-00a-my_branch
    Your branch is up to date with 'origin/MyNewGitModule-R1-00a-my_branch'.
    
    nothing to commit, working tree clean


    $ ls $sbox_mod_dir
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
 

    $ R1_00b_release_dir=$release_directory/Module-Releases/MyNewGitModule/MyNewGitModule-R1-00b

    $ ls $R1_00b_release_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h
    hey.txt
    heythere.txt
 

    $ git -P -C $R1_00b_release_dir status -b
    HEAD detached at MyNewGitModule-R1-00b
    nothing to commit, working tree clean

    $ echo 'Repo branches='
    Repo branches=
    $ git -P -C $repo_dir branch
      MyNewGitModule-R1-00-my_branch_dead
      MyNewGitModule-R1-00a-my_branch_dead
    * main

    $ echo 'Repo remote branches of R1-00b release='
    Repo remote branches of R1-00b release=
    $ git -C $R1_00b_release_dir branch -r
      origin/HEAD -> origin/main
      origin/MyNewGitModule-R1-00-my_branch_dead
      origin/MyNewGitModule-R1-00a-my_branch_dead
      origin/main

	# Check tags. Should include the first three module release.
    $ git -C $repo_dir tag
    MyNewGitModule-R1-00
    MyNewGitModule-R1-00a
    MyNewGitModule-R1-00b

    $ git -P -C $R1_00b_release_dir branch -l
    * (HEAD detached at MyNewGitModule-R1-00b)
      MyNewGitModule-R1-00a-my_branch_dead
      main

    $ cat $R1_00b_release_dir/ChangeLog
    *  somedude (glob)
    
    \t* Revision tag: R1-00b (esc)
    
    \tcommit * (esc) (glob)
    \tAuthor:* (esc) (glob)
    \tDate:   * (esc) (glob)
    
    \t    Added heythere.txt to branch (esc)
    
    *  somedude (glob)
    
    \t* Revision tag: R1-00a (esc)
    
    \tcommit * (esc) (glob)
    \tAuthor: * (esc) (glob)
    \tDate:  * (esc) (glob)
    
    \t    Added hey.txt to branch (esc)
    
    


    $ grep 'define MYNEWGITMODULE_DVERSION_RELEASE' $R1_00b_release_dir/YamVersion.h
    #define MYNEWGITMODULE_DVERSION_RELEASE "MyNewGitModule-R1-00b"


#--------------------------------------------------------------------------------
    $ echo '====== CHECK LATEST MyNewGitModule R1-00b RELEASE'
    ====== CHECK LATEST MyNewGitModule R1-00b RELEASE

# Check the latest release value

    $ $PYAM latest 'MyNewGitModule'
    MyNewGitModule R1-00b                        -  somedude    * (glob)

#--------------------------------------------------------------------------------
    $ echo '====== CHECKING OUT OLDER MyNewGitModule-R1-00a tagged module'
    ====== CHECKING OUT OLDER MyNewGitModule-R1-00a tagged module
 

    $ cd $sandbox_directory
    $ $PYAM scrap MyNewGitModule --remove

    $ $PYAM checkout MyNewGitModule  --release R1-00a --branch -

##    $ $PYAM checkout MyNewGitModule  --release main
##    $ $PYAM checkout MyNewGitModule  --branch junk

    $ sbox_mod_dir=$sandbox_directory/src/MyNewGitModule
    $ ls $sbox_mod_dir
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h
    hey.txt
 
    $ git -P -C $sbox_mod_dir status -b
    HEAD detached at MyNewGitModule-R1-00a
    nothing to commit, working tree clean
