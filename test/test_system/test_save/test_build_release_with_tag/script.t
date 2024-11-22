Test "save" command from a tagged checkout.

It makes no sense to release the SOURCES of a tagged checkout (they're already
released), but releasing the BUILD PRODUCTS makes plenty of sense, which is what
a build release is. This tests

  https://dartslab.jpl.nasa.gov/dlabbugs/show_bug.cgi?id=250

In that bug report Abhi says:

  If a tagged version of a module is checked out as a work module, running 'pyam
  save' on it errors out saying that one cannot save a tagged work module. This
  error actually does not make sense, and is currently breaking build-releases
  (since pyam-build is currently set up to check out tagged work modules).

  Clearly we do not want to release a tagged work module if it is behind or not
  in sync with the main trunk. If the tagged module corresponds to the latest
  release, then it should be in sync with the main trunk. In this case, pyam
  save should allow saving this module to make a build release. Note that
  commits are disallowed (via a commit hook) for tagged work modules, so it can
  never be ahead of the main trunk.

  The only times we should disallow saving of a tagged work module is when:

  a) the tagged module does not correspond to the latest release and is hence
  behind the main trunk.

  b) there happen to be commits on the main trunk (not the recommended way),
  which cause the tagged module to therefore be behind the main trunk.

  So we need to modify 'pyam save' to check for the above two conditions for a
  tagged work module, and if we are good with these, then the save should
  proceed. The normal save process should find that there are no new changes in
  the tagged module, and should proceed to make a build release.

Check make version is >= 4.4. If not, then we need to ignore the jobserver warnings.
    $ MAKE_VERSION=$(make --version | grep -i -c -E "GNU Make ([4-9]\.[4-9])")

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

Create a fake sandbox.

    $ sandbox_directory="$CRAMTMP/FakeSandbox"
    $ "$TESTDIR/../../../common/sandbox/make_fake_sandbox.bash" "$sandbox_directory"

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

    $ PYAM="$TESTDIR/../../../../pyam --quiet --non-interactive --no-build-server --database-connection=127.0.0.1:$PORT/test --release-directory=$release_directory --default-repository-url=$fake_repository_url"

I checkout, build and release this module.

    $ cd "$sandbox_directory"

    $ $PYAM checkout 'Dshell++'
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/featureBranches/Dshell++-R4-06g-* (glob)

    $ cd "$sandbox_directory"/src/Dshell++

Make some changes and commit them to SVN repository.

    $ svn mkdir --quiet 'my_new_directory'
    $ svn commit --quiet --message 'Add directory'

When running with "make regtest" we will get warnings like:
"make[1]: warning: jobserver unavailable: using -j1.  Add '+' to parent make rule."
However, when running with simply "srun dtest" we get nothing (no printout). We need to filter out the
warning, so we use a regex expression. However, this requires that there is a printout (even in the "srun dtest"
case). Therefore, we use an if statement to determine if this was run with "make regtest" or not, and we 
add an "echo """ accordingly.

    $ if [ -z ${MAKELEVEL+z} ] || [ $MAKE_VERSION -ne 0 ]; then
    > make -f Makefile.yam all > /dev/null && echo " "
    > else
    > make -f Makefile.yam all > /dev/null
    > fi
    \s*|\s*make\[1\]: warning: jobserver unavailable: using -j1\.  Add '\+' to parent make rule\.\s* (re)

Save

    $ cd "$sandbox_directory"
    $ $PYAM save 'Dshell++'
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

Now we check out the Dshell++ again, but I check out the RELEASE tag this time

    $ cd "$sandbox_directory"
    $ $PYAM checkout 'Dshell++' --branch -
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/releases/Dshell++-R4-06h

Make sure the right thing was checked out

    $ grep '_DVERSION_RELEASE' "$sandbox_directory/src/Dshell++/YamVersion.h" | grep Dshell
    #define DSHELL++_DVERSION_RELEASE "Dshell++-R4-06h"

    $ grep '^BRANCH_Dshell.. = Dshell..-R4-06h$' "$sandbox_directory/YAM.config"
    BRANCH_Dshell++ = Dshell++-R4-06h

I now build and try to do a save...

    $ cd "$sandbox_directory/src/Dshell++"
    $ if [ -z ${MAKELEVEL+z} ] || [ $MAKE_VERSION -ne 0 ]; then
    > make -f Makefile.yam all > /dev/null && echo " "
    > else
    > make -f Makefile.yam all > /dev/null
    > fi
    \s*|\s*make\[1\]: warning: jobserver unavailable: using -j1\.  Add '\+' to parent make rule\.\s* (re)

    $ cd "$sandbox_directory"
    $ $PYAM save 'Dshell++'
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

... I should get a build release out of it

    $ ls "$release_directory"/Module-Releases/Dshell++/Dshell++-R4-06h-Build01
    ChangeLog
    Makefile.yam
    ReleaseNotes
    YamVersion.h
    all
    my_file.txt
    my_new_directory

    $ cd "$sandbox_directory"
    $ grep -v '^#' YAM.config | grep .
    WORK_MODULES =
    LINK_MODULES = Dshell++/Dshell++-R4-06h-Build01

Great. I try again for good measure

    $ cd "$sandbox_directory"
    $ $PYAM checkout 'Dshell++' --branch -

Make sure the right thing was checked out

    $ grep '_DVERSION_RELEASE' "$sandbox_directory/src/Dshell++/YamVersion.h" | grep Dshell
    #define DSHELL++_DVERSION_RELEASE "Dshell++-R4-06h"


    $ grep '^BRANCH_Dshell' "$sandbox_directory/YAM.config"
    BRANCH_Dshell++ = Dshell++-R4-06h


I now build and try to do a save...

    $ cd "$sandbox_directory/src/Dshell++"
    $ if [ -z ${MAKELEVEL+z} ] || [ $MAKE_VERSION -ne 0 ]; then
    > make -f Makefile.yam all > /dev/null && echo " "
    > else
    > make -f Makefile.yam all > /dev/null
    > fi
    \s*|\s*make\[1\]: warning: jobserver unavailable: using -j1\.  Add '\+' to parent make rule\.\s* (re)

    $ cd "$sandbox_directory"
    $ $PYAM save 'Dshell++'
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

... I should get a build release out of it

    $ ls "$release_directory"/Module-Releases/Dshell++/Dshell++-R4-06h-Build02
    ChangeLog
    Makefile.yam
    ReleaseNotes
    YamVersion.h
    all
    my_file.txt
    my_new_directory

    $ cd "$sandbox_directory"
    $ grep -v '^#' YAM.config | grep .
    WORK_MODULES =
    LINK_MODULES = Dshell++/Dshell++-R4-06h-Build02

Now that this works consistently, I check failure modes. If we have a non-latest
tag, I barf

    $ cd "$sandbox_directory"
# $ perl -p -i -e 's/^LINK_MODULES.*/LINK_MODULES =/' YAM.config

    $ $PYAM scrap --remove Dshell++
    $ $PYAM checkout 'Dshell++' --branch - --release R4-06g

Make sure the right thing was checked out

    $ grep '_DVERSION_RELEASE' "$sandbox_directory/src/Dshell++/YamVersion.h" | grep Dshell
    #define DSHELLPP_DVERSION_RELEASE "Dshell++-R4-06g"


    $ grep  '^BRANCH_Dshell' "$sandbox_directory/YAM.config"
    BRANCH_Dshell++ = Dshell++-R4-06g


I now build and try to do a save. This should barf. This is check a.

    $ cd "$sandbox_directory/src/Dshell++"
    $ if [ -z ${MAKELEVEL+z} ] || [ $MAKE_VERSION -ne 0 ]; then
    > make -f Makefile.yam all > /dev/null && echo " "
    > else
    > make -f Makefile.yam all > /dev/null
    > fi
    \s*|\s*make\[1\]: warning: jobserver unavailable: using -j1\.  Add '\+' to parent make rule\.\s* (re)

    $ cd "$sandbox_directory"
    $ $PYAM save 'Dshell++'
    YaM error: Checked out module 'Dshell++' is for 'R4-06g' release ', while we are expecting the latest 'R4-06h release'


##    $ $PYAM save 'Dshell++' 2>/dev/null || echo fail
fail

Now I check that we cannot make a build release of a latest tagged
module if there are main trunk commits

I commit something to the trunk directly

    $ cd "$sandbox_directory/src/Dshell++"

    $ svn switch -q ^/Modules/Dshell++/trunk
    $ echo 123 > file
    $ svn add -q file
    $ svn commit -q -m 'added file' file

I switch back to my LATEST release tag

    $ cd "$sandbox_directory"
    $ $PYAM scrap --remove Dshell++

##$ rm -rf src/Dshell++
##    $ echo -c 'WORK_MODULES=\nLINK_MODULES=\n' > YAM.config
    $ $PYAM checkout 'Dshell++' --branch - --release R4-06h

Make sure the right thing was checked out

    $ grep '_DVERSION_RELEASE' "$sandbox_directory/src/Dshell++/YamVersion.h" | grep Dshell
    #define DSHELL++_DVERSION_RELEASE "Dshell++-R4-06h"


    $ grep '^BRANCH_Dshell' "$sandbox_directory/YAM.config"
    BRANCH_Dshell++ = Dshell++-R4-06h


And I try to save. I want this to barf.

    $ cd "$sandbox_directory"
    $ $PYAM save 'Dshell++'
    YaM error: Module 'Dshell++' has main trunk commits - latest R4-06h release SVN tag is '*', while trunk SVN tag is '*' (glob)

###    $ $PYAM save 'Dshell++' 2>/dev/null || echo fail
 YaM error: Module 'Dshell++' has main trunk commits - latest R4-06h release SVN tag is '*', while trunk SVN tag is '*' (glob)
 fail
