---
title: pyam
---

Copyright 2011-2024, by the California Institute of Technology. ALL
RIGHTS RESERVED. United States Government Sponsorship acknowledged. Any
commercial use must be negotiated with the Office of Technology Transfer
at the California Institute of Technology.

This software may be subject to U.S. export control laws. By accepting
this software, the user agrees to comply with all applicable U.S. export
laws and regulations. User has the responsibility to obtain export
licenses, or other export authority as may be required before exporting
such information to foreign countries or providing access to foreign
persons.

::: contents
:::

# Introduction

pyam is the Python implementation of yam. It is a utility for
configuration management and revision control.

# Installation

pyam can be installed via a standard Python `setup.py` script.

## Requirements

External dependencies required by pyam are listed below.

-   Python (\> =3.6)
-   [MySQL
    Connector/Python](https://pypi.python.org/pypi/mysql-connector-python)
    (\>= 1.1)
-   [pysvn](https://sourceforge.net/projects/pysvn/) (\>= 1.7.6)
-   [GitPython](https://pypi.org/project/GitPython/) (\>= 3.1.26)
-   GNU Make

For example, on Fedora Linux, the following command would install the
above dependencies:

    $ yum install python mysql-connector-python pysvn make

pyam talks to a repository and a database.

-   Subversion (server and repository versions \>= 1.5)
-   MySQL

pyam has been tested on Unix-like operating systems (including several
Linux distributions, OS X, and FreeBSD).

## Installation command

You can use either python 2 or python 3 to install pyam - with python 3
recommended for more recent OS. To install pyam, run (using the
appropriate python):

    $ python ./setup.py install

If you want to install it to a non-standard location:

    $ python ./setup.py install \
        --single-version-externally-managed --record=record \
        --prefix=<install_directory>

In this non-standard case, you will need to set `PYTHONPATH`
appropriately. For example, on Python 2.7, you would need to set
`PYTHONPATH` to `<install_directory>/lib/python2.7/site-packages`.

# User instructions

This section covers information for users of the pyam utility.

## Typical usage example

Below is a typical usage example. These are the commands users of pyam
would typically use on a day-to-day basis. The example assumes that
someone previously registered a new packaged with the name
`FooBarPackage`. It also assumes that the package contains a previously
registered module called `MyModule`.

Check out a sandbox:

    $ pyam setup FooBarPkg --directory my_sandbox

Run a program in the sandbox. The `srun` utility runs the program in the
sandboxed environment. It does this by finding the `Drun` script within
the sandbox and using it to set the environment variables such as `PATH`
and `LD_LIBRARY_PATH` among others:

    $ cd my_sandbox
    $ srun MyProgram

Check out a work module to do some development:

    $ pyam checkout MyModule

`MyModule` will now be checked out in a unique branch. Do some hacking:

    $ cd src/MyModule
    $ vi foo.py
    $ svn commit --message='Modify x to add feature y'
    $ vi bar.py
    $ svn commit --message='Fix bug z'

Once finished, you can `save` the module. If your branch is not on the
latest revision, you may have to sync up at this point. pyam will tell
you if this is necessary when the `save` command is issued:

    $ pyam sync MyModule

You should also make sure your link modules are up to date before
saving:

    $ pyam sync --link-modules

Or you could update all link and work modules:

    $ pyam sync --all

To save the module so that your changes become available to everyone, do
the following:

    # Always test changes before saving.
    $ make all
    $ make regtest

    $ cd ..
    $ pwd
    my_sandbox/src

    $ pyam save MyModule

If you get an error message about dangling links or out of date modules,
either fix the problem or ignore them by using the appropriate options.
To find these options use `pyam save --help`.

If you have a work module (eg, [MyModule]{.title-ref}) that you wish to
discard (\"scrap\"), use the pyam \'scrap\' command:

    $ cd <outside the module you wish to scrap>
    $ pyam scrap MyModule

This will rename the module folder by appending a timestamp and then
convert the module to a link module in your sandbox. At this point you
can delete the renamed module directory if it is no longer needed. Note
that if you wish to completely remove the module from the sandbox, you
may use the \'\--remove\' option.

## More advanced usage

For more control, edit the `YAM.config` file directly. It is contained
in the root of the sandbox. There you can specify things like which
branch you want or convert an existing work module into a link module.
Once done, you can call `pyam rebuild`.

For example:

    $ pyam setup FooBarPkg --directory my_sandbox
    $ cd my_sandbox

Edit the `YAM.config` to your specific needs. The file itself contains
some documentation at the bottom of it:

    $ vi YAM.config

Relink the link modules and rebuild the work modules. You can specify
the specific module names or you can just pass no arguments to just
rebuild everything:

    $ pyam rebuild

## Maintenance branches and releases

The DARTS Lab Q&A site has a detailed writeup of maintenance branches
and relelases. Please see <https://dartslab.jpl.nasa.gov/qa/1530>.

## Help output

To get help with command-line usage, run:

    $ pyam -h

For a more succinct output of subcommands only:

    $ pyam help

To get usage for a subcommand, run:

    $ pyam <subcommand> -h

## Question & Answer Site Help

There are a variety of questions and answers on the [DARTS Lab Q&A
Site](https://dartslab.jpl.nasa.gov/qa) that address how to use pyam.
You can search the site for \'pyam\' to see the current entries. Here
are few of the current pyam entries:

-   [How does one create a new pyam
    module?](https://dartslab.jpl.nasa.gov/qa/1544)
-   [How does one use pyam add, modify, delete the modules in a
    sandbox?](https://dartslab.jpl.nasa.gov/qa/1534)
-   [What does the pyam sync command
    do?](https://dartslab.jpl.nasa.gov/qa/1536)
-   [How can I remove a module from a
    sandbox?](https://dartslab.jpl.nasa.gov/qa/1355)
-   [What are maintenance branches and
    releases?](https://dartslab.jpl.nasa.gov/qa/1530)
-   [Is it possible to make a pyam package release with specific
    combination of module
    releases?](https://dartslab.jpl.nasa.gov/qa/1030)
-   [Is there a way to compare the difference in package definitions
    between a pair of YAM.module
    files?](https://dartslab.jpl.nasa.gov/qa/1281)
-   [How do I modify the list of modules that define a yam
    package?](https://dartslab.jpl.nasa.gov/qa/1234)
-   [Is there a command to find out which svn repository an existing
    module is located?](https://dartslab.jpl.nasa.gov/qa/1067)

Don\'t forget to log into the Q&A site in order to see the answers!

## Subcommands

Below is the list of subcommands:

    $ pyam help
    setup               set up a sandbox
    checkout            check out a link module as a work module and build it.
                        See Q&A https://dartslab.jpl.nasa.gov/qa/1534/ for
                        examples.
    rebuild             (re)build a work module
    save                release a module
    history             print the history of a module
    latest              print the latest module version
    latest-package      print the latest package version
    obsolete-builds     print the module names whose builds are obsolete
    dependencies        print the build dependencies of the module
    dependents          print the build dependents of the module
    util                miscellaneous helper options
    diff                print the diff, showing the committed changes since a
                        branch was made
    config              do various operations on sandbox configuration
                        ('YAM.config') files. NOTE: In version 1.21.4, the
                        behavior of this function changed; it no longer
                        changes the current sandbox. Its primary purpose now
                        to to create or modify YAM.config files for later use.
                        To checkout a module, use 'pyam checkout'. To convert
                        a module from a work to a link module, use 'pyam
                        scrap'.
    scrap               convert a work module to a link module and apply
                        timestamp to the old work module in the sandbox.
                        Remove the module from the sandbox if requested. See
                        Q&A https://dartslab.jpl.nasa.gov/qa/1534/ for
                        examples.
    relink              recreate symbolic links for the modules
    sync                sync up a work module to the latest revision. See Q&A
                        https://dartslab.jpl.nasa.gov/qa/1536/ for examples.
    test                test access to the repository and database
    register-new-module
                        register a new module with the repository and database
    register-new-package
                        register a new package with the repository and
                        database. NOTE: you MUST specify the package_name
                        BEFORE any --modules
    unregister-module   unregister a module from the database (for everyone)
    unregister-package  unregister a package from the database (for everyone)
    save-package        save a package. For example, to save the package with
                        the latest versions of its modules, do 'pyam save-
                        package MyPkg'. To save a specific configuration of
                        packages, create a YAM.config file and do 'pyam save-
                        package MyPkg --config <custom YAM.config file>'. This
                        command no longer requires being run in a sandbox.
    initialize          initialize pyam system
    status              print status of sandbox state
    dbutil              carry out database surgery
    help                show sub-commands

## Registering new modules

To create a new module, use the `register-new-module` command. Once this
is done, users can then check that module out:

    $ pyam register-new-module MyModule

Please see Q&A entry <https://dartslab.jpl.nasa.gov/qa/1544> for more
details, including how to select the subversion repository for the new
module.

## Registering new packages

To create a new package, use the `register-new-package` command:

    $ pyam register-new-package FooBarPkg

You can then edit `<sandbox>/common/YAM.modules` to modify what modules
belong to that package.

A shortcut is to specify the package\'s modules in the same command
using the `--modules` option:

    $ pyam register-new-package FooBarPkg --modules MyModule BingBang

By default the `SiteDefs` module will always be included automatically.
This is necessary since `SiteDefs` contains the build-system files.

## Tab-completion in bash

pyam\'s subcommands and options can be tab-completed in bash. This is
supported in pyam, if
[argcomplete](https://pypi.python.org/pypi/argcomplete) is installed.
Activate this by putting the following in `~/.bashrc`:

    eval "$(register-python-argcomplete pyam)"

## Hooks

A pre-save hook can be enabled for each module. This is done by placing
an executable in the path:

    <module>/.pyam/hooks/pre-save

The hook will be executed with the module path as the working directory.
An exit status of anything but 0 will be treated as failure.

## Differences between pyam and old yam

-   pyam provides user-friendly commands (like `checkout`). This makes
    it possible to use pyam without having to manually edit the
    `YAM.config`.
-   pyam does not rely on client\'s local time. Everything is based on
    the MySQL server\'s time.
-   pyam calls both `all` and `alltgt-all` Make rules so that builds
    work on non-NFS drives.
-   By default pyam\'s output is succinct to avoid confusing the user
    with irrelevant information.
-   Diffs can be shown in the email release notifications.
-   Long output text are automatically piped into a pager (`less`).
-   The `diff` command colorizes the output if called interactively in
    the shell.

## Automated build releases

If module A depends on module B, then if A\'s header files get modified,
B would probably need to be rebuilt. To automate the detection of this
situation and build modules as necessary, use the `pyam-build` script:

    $ pyam-build

It will detect which modules have obsolete builds and make build
releases of them.

This can be run in the background on some server. In this mode, it is
useful to run it in a loop like:

    $ pyam-block-until-release 'pyam-build'

If you have modules that all modules depend on, but are not detected by
pyam, you can specify them explicitly:

    $ pyam-block-until-release 'pyam-build --dependencies MyModuleA MyModuleB'

This is useful for cases things like build-related scripts. Scripts are
not header files, so they are not automatically detected as
dependencies.

# Administrator instructions

This section covers information for the administrator who will be
installing and configuring pyam.

## Prerequisites

Before configuring pyam, you should start a MySQL server and an
Subversion repository. The location of these items will be used in
configuring pyam.

pyam expects a database to exist on the MySQL server. Once you have a
MySQL server up, all you need to do is create an empty database. The
`database_name`, `username`, and `password` you use will be referenced
in the pyam configuration. For example, a MySQL command you could use to
create a database named `database_name` with `username` granted access
is:

    mysql> create database database_name;

    mysql> create user 'username'@'%' identified by 'password';
    mysql> grant all privileges on database_name.* to 'username'@'%' identified by 'password';
    mysql> grant all privileges on database_name.* to 'username'@'hostname' identified by 'password';
    mysql> flush privileges;

Note that the second `grant` is for running `pyam` from the host itself.

pyam works with any Subversion protocol (`svn://`, `https://`,
`file://`). The repository URL will be referenced in the pyam
configuration file. The simplest one, which doesn\'t require a server,
is the `file://` protocol. For example, you could simply create a
repository with:

    $ svnadmin create my_repository_path

    $ svn ls file://my_repository_path

## Configuration

The top-level command-line options for pyam can be put in a
configuration file. For example, in the lines below, we set the defaults
for command-line options including `--database-connection` and
`--default-repository-url`:

    [pyam]
    database-connection=username:password@127.0.0.1:3306/database_name

    default-repository-url=file://my_repository_path

    release-directory=/home/blah/release_directory

    email-server=smtp.fakeurl.gov:25
    email-to-address=email.list@fakeurl.gov

The above contents can be put in a file. That file will be found by pyam
via the environment variables `YAM_PROJECT_CONFIG_DIR`, and
`YAM_PROJECT`. This behavior is inherited from old yam for backward
compatibility. pyam will look for the configuration file at:

    $YAM_PROJECT_CONFIG_DIR/$YAM_PROJECT.pyamrc

For example, if `YAM_PROJECT_CONFIG_DIR` is defined as `/home/blah` and
`YAM_PROJECT` is defined as `my_project`, pyam will look for:

    /home/blah/my_project.pyamrc

To discover all the options or to see if your configuration is properly
read in, run:

    $ pyam --help

which should print your configuration in the `(default: *)` lines.

## Older Subversion repositories

Subversion repositories prior to version 1.5 do not have support for
merge tracking. pyam normally makes use of Subversion\'s merge tracking
to provide better output for `svn log` and to do merging more cleanly.
But pyam can also run in fallback mode, where it does not rely on merge
tracking. To enable this, specify your repository version in your pyam
configuration file. Any version prior to 1.5 will trigger the fallback
behavior. For example:

    repository-version=1.2.1

Note that, since older Subversion repositories don\'t support merge
tracking, when you do a `pyam sync`, Subversion won\'t carry over your
old commit messages. So you will have to enter your commit messages
again (after the sync) for them to show up in the `ChangeLog` file. (On
repositories with merge tracking, Subversion will automatically carry
over the commit messages from the old branch into the new merged
branch.)

## Testing database and repository access

Once configured, we can test whether pyam can access the database and
the default repository by running:

    $ pyam test

If successful, pyam will print out something like this:

    Database access: succeeded
    Default repository access: succeeded

## Environment variables

Some configuration must be done via environment variables. This is
because the Make build system needs access to the variables (when called
manually by the user as in `make all`). These variables are:

    YAM_SITE - A name given to the site (e.g., "telerobotics")
    YAM_NATIVE - A string that represents the operating system name
                 (e.g., "x86_64-fedora15-linux")
    YAM_TARGET - Typically same as YAM_NATIVE (unless cross compiling)

## Initialization

After configuration is complete, and the repository and database servers
are running, we can initialize them for pyam. This need only be done
once to set up the database tables and repository directories. This is
something the administrator would typically do rather than everyday
users. To do the initialization, call:

    $ pyam initialize

Calling it twice will have no effect the second time. Once this is done,
users can start using pyam.

## Build-system customization

The build system is contained in the [SiteDefs]{.title-ref} module.
Create a sandbox and check out [SiteDefs]{.title-ref} to customize the
build system:

    $ pyam setup --directory my_sandbox --modules SiteDefs
    $ cd my_sandbox
    $ pyam checkout SiteDefs

The makefiles need to be customized to support building using GCC. These
files are where you can specify third-party library paths, build flags,
and other things. This is done by setting the variables in several
makefiles:

    SiteDefs/mkHome/auto/site.env
    SiteDefs/mkHome/auto/<site>-site-supported.mk

    SiteDefs/sites/shared.mk

    SiteDefs/sites/<site>/site-config-<target_os>
    SiteDefs/sites/<site>/site.local

    SiteDefs/targets/<target_os>.mk

After customization is done and files are committed, save the
[SiteDefs]{.title-ref} module:

    $ pyam save SiteDefs

This will make the changes available to all users.

# Developer information

This section covers information for the developers of the pyam tool
itself.

## Design

Classes were designed with testability in mind. Most classes don\'t talk
to concrete classes directly, but instead they talk to interfaces.
Concrete objects are passed in their constructors. We don\'t use
inheritance unless we plan to implement an abstract method. We never use
static methods. We use (non-member) functions instead.

Most of the interfaces talk to external entities like databases and file
systems. These interfaces are listed below.

-   BuildSystem
-   ConfigurationReader
-   ConfigurationWriter
-   DatabaseReader
-   DatabaseWriter
-   FileSystem
-   RevisionControlSystem

The concrete implementations are listed below.

-   MakeBuildSystem
-   ConcreteConfigurationReader
-   ConcreteConfigurationWriter
-   SQLDatabaseReader
-   SQLDatabaseWriter
-   LocalFileSystem
-   SVNRevisionControlSystem

None of these concrete classes talk directly to each other. Other
concrete classes are passed in via their constructors. This avoids any
dependency between concrete classes and thus modularity.

Building on top of the interfaces are the yam module and yam package
classes. These are listed below.

-   Module
-   BranchedWorkModule
-   MainWorkModule
-   TaggedWorkModule
-   WorkModule
-   Sandbox
-   LooseSandbox
-   MainPackageSandbox
-   PackageSandbox
-   TaggedPackageSandbox

In their constructors they take some subset of the previously mentioned
interfaces. None of these module and package classes talk directly to
the file system, database, or repository. They talk only to the
interfaces. This loose coupling makes them easy to unit test. We can
verify their behavior without having to look at files or query
databases.

The naming convention of the code follows [PEP
8](https://www.python.org/doc/essays/styleguide).

## Testing

The automated test suite is contained in the `test` directory.

Each module has its own set of unit tests. Each class/function is tested
in isolation from all/most other classes/functions.

We also have system tests for pyam. These tests are done against a
temporary MySQL server and SVN repository. Before each system test, we
launch a script that creates and launches the temporary server and
repository. Each pyam subcommand (`setup`, `rebuild`, `latest`, etc.) is
tested in these system tests.

There are also tests that do static analysis. We run the usual pep8,
pyflakes, and pylint. In addition to these, we run custom static
analysis to enforce higher-level design decisions.

## Exceptions

Exceptions that are meant to bubble back up to the user calling `pyam`
are derived from YamException. Exceptions that should never bubble up
and should always be handled at the lower levels are prefixed with the
word `Internal` and are not derived from YamException.

## Things inherited from old yam (for backward compatibility)

-   `YAM_PROJECT_CONFIG_DIR` environment variable.
-   Naming of revision tags with things like `R1-00a` instead of just
    using a number.
-   Using of non-standard Subversion repository structure.
    (`featureBranches`, `releases`, `trunk`) should really be
    (`branches`, `tags`, `trunk`).

# Troubleshooting

Below are various troubleshooting hints.

## pyam hangs on `pyam diff`

This can happen if you modify your global Subversion configuration to
use a non-standard `diff-cmd`. Don\'t do this as it even affects
programs other than the `svn` command-line utility that merely use
Subversion bindings.

## MySQL says `Client does not support authentication protocol`

See <https://dev.mysql.com/doc/refman/4.1/en/old-client.html>.

## pyam crashes with `Negative size passed to PyString_FromStringAndSize`

If you are getting this during a `save` or `diff`, you probably added a
file to the repository so large that Python/pysvn is running out of
memory or overflowing some buffer. We\'ve seen this once on a low memory
machine when someone added a multiple gigabyte file to the repository
and tried to save that module.

## Characters like `^M` show up in the pyam progress output

You are probably running in some non-standard terminal (like emacs). Set
the `TERM` environment variable to `dumb` to disable the spinning
activity in the `--->` progress messages.

## pyam says `Waiting for exclusive use of sandbox`

The lock file indicates that there is some other pyam process running
and modifying the sandbox. If not, then probably a previous pyam got
killed with `kill -9`. In the latter case, you\'ll need to manually
remove the lock file.

## pyam says `Uncommitted files`

Commit your files with `svn commit`. If you get the following, then it
means that you need to commit the Subversion metadata:

    $ svn status
    M      .

You commit it by running `svn commit .`.

## Sort `latest` by date

    $ pyam latest | sort -k5

## Put boolean flags in configuration file

For things like `--require-bug-id`, to enable it in the configuration
file, add the following:

    [pyam]
    require-bug-id=x

To disable, just remove the line.

To invoke flags like `--no-release-notes` in the configuration file:

    [pyam]
    release-notes=

## Configure to avoid text-editor prompt for release note message

Set the text editor to be the POSIX `false` program:

    [pyam]
    text-editor=false

# Bug reports

Please report bugs (in pyam or in this document) to Abhi Jain
\<<jain@jpl.nasa.gov>\>.
