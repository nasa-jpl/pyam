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
Set up the "YAM.config" before saving.

    $ tmp_sandbox_directory="$CRAMTMP/tmp_sandbox"
    $ $PYAM setup --directory="$tmp_sandbox_directory" MyNewPkg
    $ pushd "$tmp_sandbox_directory" > /dev/null
    $ echo '# Hello.' >> YAM.config
    $ grep 'SimScape' "$tmp_sandbox_directory/YAM.config"
                   SimScape/SimScape-R1-00 \
    # BRANCH_SimScape = SimScape-R1-00  * (glob)

    $ svn commit --quiet --message 'Save YAM.config before saving package'
    $ popd > /dev/null

-----------------------------------------------------------------------------
Test "save-package".

    $ $PYAM save-package --config-file "$tmp_sandbox_directory/YAM.config" --release-note-message='Fake message' MyNewPkg
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

Verifying that "YAM.config" is untouched by checking out a tagged package.

    $ sandbox_directory="$CRAMTMP/sandbox"
    $ $PYAM setup --directory="$sandbox_directory" --revision-tag='R1-00a' MyNewPkg

    $ ls -d "$sandbox_directory" > /dev/null
    $ grep 'SimScape' "$sandbox_directory/YAM.config"
                   SimScape/SimScape-R1-00 \
    # BRANCH_SimScape = SimScape-R1-00  * (glob)

    $ grep '# Hello.' "$sandbox_directory/YAM.config"

    $ diff --unified "$tmp_sandbox_directory/YAM.config" "$sandbox_directory/YAM.config"
    --- */tmp_sandbox/YAM.config* (glob)
    +++ */sandbox/YAM.config* (glob)
    @@ -62,4 +62,3 @@
     # action is to branch off the latest release appending hyphen-login for the
     # branch name. So if the latest version of MyModule is "MyModule-R1-05", then
     # branch tag might default to "MyModule-R1-05-my_branch".
    -# Hello.

    $ ls -d "$sandbox_directory/Makefile"
    */sandbox/Makefile (glob)
    $ ls -d "$sandbox_directory/common"
    */sandbox/common (glob)

Check that the sandbox directory is checked out from "Packages/.../releases"

    $ svn info --show-item relative-url $sandbox_directory
    ^/Packages/MyNewPkg/releases/MyNewPkg-R1-00a


Check that the sandbox directory is checked out from "Packages/.../releases/.../common"

    $ svn info --show-item relative-url "$sandbox_directory/common"
    ^/Packages/MyNewPkg/releases/MyNewPkg-R1-00a/common


Make sure our release note is in there.

    $ grep 'Fake message' "$sandbox_directory/ReleaseNotes"
    \tFake message (esc)
