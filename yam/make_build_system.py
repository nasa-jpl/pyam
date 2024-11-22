"""Contains the MakeBuildSystem class."""

from __future__ import absolute_import
from __future__ import division

import contextlib
import locale
import os
import shlex
import shutil
import subprocess
import textwrap
import threading
import time

from . import build_system
from . import yam_exception
from . import yam_log


class MakeBuildSystem(build_system.BuildSystem):
    """A Make implementation of build_system.

    We call both the regular rule and the rule prefixed with "alltgt" (all
    targets). This is because the "alltgt" doesn't work when dealing with
    non-NFS locations.

    """

    def __init__(
        self,
        native_operating_system,
        site_name,
        use_build_server=True,
        progress_callback=None,
        jobs=0,
    ):
        """Initialize.

        If progress_callback is specified, build status will be passed to it.

        progress_callback takes two parameters. The first is the elapsed build
        time. The second is a boolean that is True when the build is complete.

        """
        build_system.BuildSystem.__init__(self)

        self.__native_operating_system = native_operating_system
        self.__site_name = site_name
        self.__use_build_server = use_build_server
        self.__progress_callback = progress_callback

        # Avoid trying to constantly ssh into build server. That causes
        # performance issues.
        self.__build_server_accessible_cache = {}

        self.__jobs = jobs
        if self.__jobs <= 0:
            import multiprocessing

            self.__jobs = multiprocessing.cpu_count()

    def build(self, module_names, sandbox_directory):
        """Implementation of build_system.build()."""
        # build() needs progress_callback since it can take a while.
        return _call_make(
            directory=sandbox_directory,
            rule="all",
            module_names=module_names,
            use_build_server=self.__use_build_server,
            native_operating_system=self.__native_operating_system,
            jobs=self.__jobs,
            site_name=self.__site_name,
            progress_callback=self.__progress_callback,
        )

    def clean(self, module_names, sandbox_directory):
        """Implementation of build_system.clean()."""
        return _call_make(
            directory=sandbox_directory,
            rule="clean",
            module_names=module_names,
            use_build_server=self.__use_build_server,
            native_operating_system=self.__native_operating_system,
            jobs=self.__jobs,
            site_name=self.__site_name,
            progress_callback=self.__progress_callback,
        )

    def make_links(self, module_names, sandbox_directory, release_directory):
        """Implementation of build_system.make_links()."""
        # SiteDefs is a special case that needs a remove links to be done. For
        # whatever reason, SiteDefs' "mklinks" rule does not create the link.
        # (Above is not true, mklinks will create SiteDefs link)
        # Rather, its "rmlinks" rule actually creates the SiteDefs link.
        success = True

        # remove old links for the modules
        success = success and _call_make(
            directory=sandbox_directory,
            rule="mklinks",
            module_names=module_names,
            use_build_server=self.__use_build_server,
            release_directory=release_directory,
            native_operating_system=self.__native_operating_system,
            jobs=self.__jobs,
            site_name=self.__site_name,
            progress_callback=self.__progress_callback,
        )

        # create links for the modules
        success = success and _call_make(
            directory=sandbox_directory,
            rule="mklinks",
            module_names=module_names,
            use_build_server=self.__use_build_server,
            release_directory=release_directory,
            native_operating_system=self.__native_operating_system,
            jobs=self.__jobs,
            site_name=self.__site_name,
            progress_callback=self.__progress_callback,
        )

        return success

    def remove_links(self, module_names, sandbox_directory, release_directory):
        """Implementation of build_system.remove_links()."""
        return _call_make(
            directory=sandbox_directory,
            rule="rmlinks",
            module_names=module_names,
            use_build_server=self.__use_build_server,
            native_operating_system=self.__native_operating_system,
            jobs=self.__jobs,
            site_name=self.__site_name,
            release_directory=release_directory,
            progress_callback=self.__progress_callback,
        )

    def create_build_files(
        self,
        path,
        release_directory,
        operating_system_name,
        top_level_file_callback=lambda _: None,
    ):
        """Implementation of build_system.create_build_files()."""
        site_defs_directory = os.path.join(os.path.dirname(__file__), "make_build_system_data", "SiteDefs")

        # Copy files while ignoring hidden files/directories.
        for filename in os.listdir(site_defs_directory):
            if filename.startswith("."):
                continue  # pragma: NO COVER

            source_path = os.path.join(site_defs_directory, filename)
            destination_path = os.path.join(path, filename)
            if os.path.isdir(source_path):
                shutil.copytree(
                    src=source_path,
                    dst=destination_path,
                    symlinks=True,
                    ignore=shutil.ignore_patterns(".*"),
                )
            else:
                shutil.copy2(src=source_path, dst=destination_path)

            # Make sure specific files are executable.
            make_children_executable(path=destination_path, extensions=[".pl", ".sh", ".bash"])

            top_level_file_callback(destination_path)

        # <output_path>/mkHome/auto/site.env
        generate_site_environment_file(
            module_release_directory=release_directory,
            operating_system_name=operating_system_name,
            output_filename=os.path.join(path, "mkHome", "auto", "site.env"),
            top_level_file_callback=top_level_file_callback,
        )

        # <output_path>/mkHome/auto/<site>-site-supported.mk
        generate_supported_site_files(
            operating_system_name=operating_system_name,
            output_filename=os.path.join(path, "mkHome", "auto", self.__site_name + "-site-supported.mk"),
            top_level_file_callback=top_level_file_callback,
        )

        # Create this directory before the below files, which are contained in
        # this directory.
        site_base_path = os.path.join(path, "sites")
        os.mkdir(site_base_path)
        top_level_file_callback(site_base_path)

        # <output_path>/sites/shared.mk
        generate_site_shared_file(
            output_filename=os.path.join(site_base_path, "shared.mk"),
            top_level_file_callback=top_level_file_callback,
        )

        site_path = os.path.join(site_base_path, self.__site_name)
        os.mkdir(site_path)
        top_level_file_callback(site_path)
        del site_base_path

        # <output_path>/sites/<site>/site-config-<target_os>
        generate_site_target_configuration_file(
            output_filename=os.path.join(site_path, "site-config-{os}".format(os=operating_system_name)),
            top_level_file_callback=top_level_file_callback,
        )

        # <output_path>/sites/<site>/site.local
        generate_site_local_file(
            output_filename=os.path.join(site_path, "site.local"),
            top_level_file_callback=top_level_file_callback,
        )

        # Create this directory before the below files, which are contained in
        # this directory.
        target_path = os.path.join(path, "targets")
        os.makedirs(target_path)
        top_level_file_callback(target_path)

        # <output_path>/targets/<target_os>.mk
        generate_target_file(
            output_filename=os.path.join(target_path, operating_system_name + ".mk"),
            top_level_file_callback=top_level_file_callback,
        )

    def create_module_files(self, module_name, module_path, top_level_file_callback=lambda _: None):
        """Check out trunk and add basic files.

        Return the working copy path.

        """
        makefile_yam_path = os.path.join(module_path, "Makefile.yam")
        with open(makefile_yam_path, "w") as output_file:
            output_file.write(_MODULE_MAKEFILE_CONTENTS)
        top_level_file_callback(makefile_yam_path)
        del makefile_yam_path

        makefile_path = os.path.join(module_path, "Makefile")
        os.symlink("Makefile.yam", makefile_path)
        top_level_file_callback(makefile_path)
        del makefile_path

        def add_empty_file(filename):
            """Create and add empty filename."""
            local_path = os.path.join(module_path, filename)
            with open(local_path, "w") as output_file:
                output_file.write("\n")
            top_level_file_callback(local_path)

        for f in ["YamVersion.h", "ChangeLog"]:
            add_empty_file(f)

        release_note_path = os.path.join(module_path, "ReleaseNotes")
        wrapped_description = textwrap.fill(
            """This file documents API, usage, portability etc.
changes that have been introduced in new versions of the "{module}" module.
This information should be kept in mind when upgrading to newer versions of
the module. This file may also document major bug fixes in so far as they
may impact upgrade decisions. More complete and detailed information on
changes to the "{module}" module can be found in the ChangeLog file.""".format(
                module=module_name
            ),
            width=79,
            break_long_words=False,
        ).strip()

        with open(release_note_path, "w") as f:
            f.write(
                """Release notes for "{module}" module

{description}

Release R1-00:

\tCreate module
""".format(
                    module=module_name, description=wrapped_description
                )
            )

        top_level_file_callback(release_note_path)
        del release_note_path

    def build_dependencies(self, module_path, release_directory):
        """Implementation of build_system.build_dependencies()."""
        return find_module_dependencies(
            module_name=os.path.split(module_path)[1],
            sandbox_directory=os.path.split(os.path.split(module_path)[0])[0],
            release_directory=release_directory,
        )

    def check_build_server(self, sandbox_directory):
        """Implementation of build_system.check_build_server."""
        return self._check_build_server(sandbox_directory, None)

    def _check_build_server(self, sandbox_directory, native_operating_system):
        """Return True if build server is up.

        Return False if the server is running the same operating system
        as the local machine.

        """
        if sandbox_directory not in self.__build_server_accessible_cache:
            self.__build_server_accessible_cache[sandbox_directory] = _check_build_server(
                sandbox_directory, native_operating_system
            )

        return self.__build_server_accessible_cache[sandbox_directory]


def parse_dependency_file(filename):
    """Parse GCC (*.d) dependency file.

    Return list of dependency paths.

    """
    try:
        with open(filename) as input_file:
            # Split up the .d file's contents into tokens and remove
            # blank tokens. Use try/except in case the .d file was not a
            # compiler generated dependency file
            tokens = []
            try:
                tokens = [t.strip() for t in shlex.split(input_file.read()) if t.strip()]
            except:
                yam_log.say("Unable to extract dependendy info from {} - skipping".format(filename))

            if not tokens:
                return []

            try:
                # Handle 2 formats for the .d files:
                # Previously first item is the name of the dependency
                #     filename itself followed by the associated file
                #     and then a ':'
                # As of 10/16/2016 something has changed, so that .d
                #     file is no long there, so that
                #     the first item has the : at the end
                if tokens[0].strip().endswith(":"):
                    # new style .d file
                    deps = tokens[1:]
                elif tokens[1].strip().endswith(":"):
                    # old style .d file
                    deps = tokens[2:]
                else:
                    # Not a valid dependency file.
                    deps = []

                return deps
            except IndexError:
                return []
    except (IOError, UnicodeDecodeError):
        # Either the file is not readable or it is not a text file.
        return []


def full_split(path):
    """Return path split into tuple of directories.

    Opposite of os.path.join().

    """
    reverse_paths = []
    while path:
        (path, tail) = os.path.split(path)
        reverse_paths.append(tail)
        if path == "/":
            reverse_paths.append("/")
            break

    return tuple(reversed(reverse_paths))


def extract_module_dependencies(dependency_paths, module_name, sandbox_directory, release_directory):
    """Return dictionary of dependencies.

    The keys will be the module names. The values are sets of files in
    that module that we depend on.

    """
    sandbox_directory = os.path.realpath(sandbox_directory)

    if release_directory:
        release_directory = os.path.realpath(release_directory)

    dependencies = {}
    for path in dependency_paths:
        # Resolve relative paths. They are with respect to the module.
        if not path.startswith("/"):
            path = os.path.join(sandbox_directory, "src", module_name, path)

        # We need the canonical path to compare properly.
        path = os.path.realpath(path)

        relative_path = os.path.relpath(path, start=sandbox_directory)
        name = None
        filename = None
        if relative_path.startswith("src/"):
            # dependency is on a file located in a work module in this sandbox
            name = full_split(relative_path)[1]
            filename = os.path.basename(relative_path)
        elif release_directory:
            # dependency is on a file located in the module release area
            relative_path = os.path.relpath(path, start=release_directory)
            if relative_path.startswith("Module-Releases/"):
                name = full_split(relative_path)[1]
                filename = os.path.basename(relative_path)

        if name and name != module_name:
            try:
                dependency_set = dependencies[name]
            except KeyError:
                dependency_set = set()

            dependency_set.add(filename)
            dependencies[name] = dependency_set

    return dependencies


def find_module_dependencies(module_name, sandbox_directory, release_directory):
    """Return module dependencies.

    Do this by finding and extracting information from GCC dependency
    files.

    """
    module_path = os.path.join(sandbox_directory, "src", module_name)

    import fnmatch

    # recursively find all .d files in the modules from
    # http://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python
    # need this because the .o and .d files are now located at the same
    # relative position as the source files they came from - so could be
    # at arbitrary levels deep
    dependency_paths = []
    for found in os.walk(module_path):
        root = found[0]
        filenames = found[2]
        for filename in fnmatch.filter(filenames, "*.d"):
            fpath = os.path.join(root, filename)
            dependency_paths += parse_dependency_file(fpath)

    return extract_module_dependencies(
        dependency_paths=dependency_paths,
        module_name=module_name,
        sandbox_directory=sandbox_directory,
        release_directory=release_directory,
    )


def _make_command(
    directory,
    rule,
    additional_arguments,
    module_names,
    jobs,
    site_name,
    release_directory,
):
    """Return the appropriate Make command as a list of arguments."""

    arguments = [
        rule,
        "MODULES={m}".format(m=" ".join(module_names)),
        "-j{load}".format(load=jobs),
        "-k",
        "YAM_SITE={}".format(site_name),
    ] + additional_arguments

    # We use is not None since release_directory could be an empty string.
    if release_directory:
        module_release_directory = os.path.join(release_directory, "Module-Releases")
        if not os.path.exists(module_release_directory):
            raise yam_exception.YamException(
                "Module release directory {d} does not exist".format(d=module_release_directory)
            )

        arguments.append("YAM_VERSIONS={d}".format(d=module_release_directory))

    # Don't put quotes around the module list
    command_list = ["make", "--directory", directory] + arguments

    return command_list


def _safe_environment_variables():
    """Return all environment variables except unsafe ones.

    "YAM_ROOT" will cause problems if pyam's definition of it gets
    transferred to the Make system. "YAM_VERSIONS" could interfere with
    our "YAM_VERSIONS" Make argument due to idiosyncrasies of Make.

    """
    return dict((k, os.environ[k]) for k in os.environ.keys() if k not in ["YAM_ROOT", "YAM_VERSIONS"])


def _check_build_server(sandbox_directory, native_operating_system):
    """Return True if build server is accessible."""
    with open(os.devnull, "w") as dev_null:
        process = subprocess.Popen(
            ["make", "--quiet", "--directory=" + sandbox_directory, "rshtest"]
            + (["SKIP_ALLTGT_TARGETS=" + native_operating_system] if native_operating_system else []),
            env=_safe_environment_variables(),
            stdout=subprocess.PIPE,
            stderr=dev_null,
        )

    return "success" in process.communicate()[0].decode(locale.getpreferredencoding(False)).lower()


def _call_make(
    directory,
    rule,
    module_names,
    use_build_server,
    native_operating_system,
    jobs,
    site_name,
    release_directory=None,
    progress_callback=None,
):
    """Call with regular rule and also "alltgt".

    Return True if successful.

    """
    if not os.path.exists(os.path.join(directory, "Makefile")):
        raise yam_exception.YamException("Directory '{}' is missing a 'Makefile'".format(directory))

    all_rules = [rule]
    arguments = []

    success = True
    for r in all_rules:
        # Run the rules one at a time to avoid risking file clobbering.
        result = _call_make_single(
            directory=directory,
            arguments=arguments,
            rule=r,
            module_names=module_names,
            jobs=jobs,
            site_name=site_name,
            release_directory=release_directory,
            progress_callback=progress_callback,
        )

        success = success and result

    return success


def _call_make_single(
    directory,
    rule,
    arguments,
    module_names,
    jobs,
    site_name,
    release_directory,
    progress_callback,
):
    """Call the Make program.

    Return True if successful.

    """

    def run_process():
        """Run "make".

        Make sure environment variable "YAM_ROOT" is not defined.
        Note that trying to unset the "YAM_ROOT" variable at the Make
        command-line won't work. Code in the Makefile that tries to set the
        variable will fail.

        """
        command = _make_command(
            directory=directory,
            rule=rule,
            additional_arguments=arguments,
            module_names=module_names,
            jobs=jobs,
            site_name=site_name,
            release_directory=release_directory,
        )

        yam_log.enter("Invoking {}".format(command))
        if module_names:
            yam_log.say("Running make {}".format(rule) + " for {}".format(module_names) + " modules.")
        else:
            yam_log.say("Running make {}".format(rule))

        returncode = 0
        try:
            output = subprocess.check_output(
                command,
                env=_safe_environment_variables(),
                stderr=subprocess.STDOUT,
            )
        except OSError as exception:  # pragma: NO COVER
            yam_log.lexit("OSError!")
            raise yam_exception.YamException("{}: {}".format(exception, command))  # pragma: NO COVER
        except subprocess.CalledProcessError as e:
            returncode = e.returncode
            output = e.output

        yam_log.lexit(
            "returncode: {}. Output:\n".format(returncode) + "v" * 35 + "\n" + str(output) + "\n" + "^" * 35 + "\n"
        )

        return 0 == returncode

    with _progress_context_manager(progress_callback, rule):
        return run_process()


@contextlib.contextmanager
def _progress_context_manager(progress_callback, rule):
    """Parse Make output and passes status to progress_callback."""
    if progress_callback:

        class Spinner(threading.Thread):
            """Threaded spinner."""

            def __init__(self):
                """Initialize."""
                threading.Thread.__init__(self)
                self.__exit_event = threading.Event()

            def run(self):
                start_time = time.time()
                while not self.__exit_event.is_set():
                    progress_callback(time.time() - start_time, False, rule)
                    self.__exit_event.wait(5)

            def stop(self):
                """Stop the spinner."""
                self.__exit_event.set()

        spinner = Spinner()
        spinner.start()

        try:
            yield
        finally:
            spinner.stop()
            spinner.join()

        progress_callback(0.0, True, rule)
    else:
        yield


def generate_file(output_filename, top_level_file_callback, string_content):
    """Generate file and call callback."""
    with open(output_filename, "w") as output_file:
        output_file.write(string_content)

    top_level_file_callback(output_filename)


# TODO: Factor out common code below
def generate_site_environment_file(
    module_release_directory,
    operating_system_name,
    output_filename,
    top_level_file_callback,
):
    """Generate site environment file.

    This will be written to

        <output_path>/mkHome/auto/site.env

    """
    generate_file(
        output_filename=output_filename,
        top_level_file_callback=top_level_file_callback,
        string_content=r"""
# site.env - set default values for YAM variables
# YAM_SITE, YAM_NATIVE, YAM_TARGET, YAM_OS
#
# include this file from a Makefile

#===========================================================
# standard Make options
# this variable can be overridden from the command line to make
# builds stop on error
MAKEOPTS ?= i
MAKEFLAGS := rR$(MAKEOPTS)

# parallel build option
# can be overridden from the command line
YAM_MKPLL ?= -j -l 4

# turn off all implicit rules
.SUFFIXES:

#==================================================================
# Initialize some of the standard variables.

# Used in Makefile.top and bldRules.mk.
ALLTGT ?=

# Function to pretty print target/host information for parallel makes.
hostsstr = $(foreach t,$(1),printf "\t%20s -> %s\n" $(t) $(COMPILE_HOST-$(t)))

#===========================================================
# this is the default rule
help::

#===========================================================
# Rules for modules for that execute for supported as well as unsupported
# targets work modules only.
YAM_ALLTGT_WORKMOD_RULES := clean
# work and link modules
YAM_ALLTGT_RULES := docs

# rules for both work and link modules
YAM_LINKMOD_RULES := regtest pllregtest

# rules for only work modules (for supported targets)
YAM_BUILD_RULES := links libs libsso bins
YAM_WORKMOD_RULES := $(YAM_BUILD_RULES)


#===========================================================
# This has to be customized for each site.
# export this variable since it is needed by module-dependencies.pl
export YAM_VERSIONS ?= {module_release_directory}

# set list of all known YAM targets
# Be sure add a space before and after each element of this list. This
# will help avoid findstring from finding a match for an element suac
# as sparc-sunos5 when finding sparc-sunos5.6
#
ALL_YAM_OS := unix vx
unix_targets := {operating_system_name}
vx_targets :=
ALL_YAM_TARGETS := $(unix_targets) $(vx_targets)

#===========================================================
# determine native platform
# if YAM_TARGET is specified and is a unix target, and not a
# cross-compile target then set YAM_NATIVE to its value
ifdef YAM_TARGET
    ifeq ($(filter $(YAM_TARGET),$(vx_targets)),)
        ifneq ($(filter $(YAM_TARGET),$(unix_targets)),)
            YAM_NATIVE = $(YAM_TARGET)
        endif
    endif
endif

ifeq ($(YAM_NATIVE),)
    YAM_NATIVE := $(shell $(SITEDEFSHOME)/mkHome/shared/yamNative.sh)
endif

export YAM_NATIVE

#===========================================================
# determine target platform
# this is where the executables should run
# normally this is the same as the native platform unless compiling for VxWorks

YAM_TARGET ?= $(YAM_NATIVE)
export YAM_TARGET

#===========================================================
# determine target OS
ifneq ($(filter $(YAM_TARGET),$(unix_targets)),)
    YAM_OS := unix
else
    YAM_OS := vx
endif

ifeq ($(YAM_TARGET),i486-cygwin)
    YAM_OS_TMP := windows
endif

ifeq ($(YAM_TARGET),i486-visualc)
    YAM_OS_TMP := windows
endif

YAM_OS ?= unknown
export YAM_OS

#===========================================================
# the command to access remote hosts
RSHCMD ?= ssh
export RSHCMD
""".lstrip().format(
            module_release_directory=module_release_directory,
            operating_system_name=operating_system_name,
        ),
    )


def generate_supported_site_files(operating_system_name, output_filename, top_level_file_callback):
    """Generate supported site file."""
    generate_file(
        output_filename=output_filename,
        top_level_file_callback=top_level_file_callback,
        string_content=r"""
# Defines the following optional variables that specify the
# supported/unsupported targets for the site.
#
# Keep in mind that these settings are included in after the
# module's optional .supported.mk file has been included to set
# these same variables.

# The SITE_RELEASES_DIR variable points to the module/packages releases area
# specific to this site.

# These variables restrict the available list of targets.
SITE_SUPPORTED_TARGETS := {operating_system_name}

# Host computer to use (with rsh) when building for each target architecture
# (when the current host does not build the desired target).
COMPILE_HOST-{operating_system_name} :=
""".lstrip().format(
            operating_system_name=operating_system_name
        ),
    )


def generate_site_target_configuration_file(output_filename, top_level_file_callback):
    """Generate supported site file."""
    generate_file(
        output_filename=output_filename,
        top_level_file_callback=top_level_file_callback,
        string_content=r"""
########################################################################
#
# !!!!!! EDIT & CUSTOMIZE THIS FILE !!!!!!
#
########################################################################
#
# this file defines build flags that are specific to a
# build target for a specific YaM site.
# It should be customized for each site/target combination.

#==========================================================
# include site specific stuff
include $(SITEDEFSHOME)/sites/$(YAM_SITE)/site.local

#==========================================================
# add other flag settings that are specific to this site/target build
""".lstrip(),
    )


def generate_site_local_file(output_filename, top_level_file_callback):
    """Generate site local file."""
    generate_file(
        output_filename=output_filename,
        top_level_file_callback=top_level_file_callback,
        string_content=r"""
########################################################################
#
# !!!!!! EDIT & CUSTOMIZE THIS FILE !!!!!!
#
########################################################################
#
# Defines build flags specific for a YaM site.
#
# This file is typically included by the individual site/target
# specific site-config-<target> files

#==========================================================
# load in generic flag settings
include $(SITEDEFSHOME)/sites/shared.mk

# Add additional flag definitions here
""".lstrip(),
    )


def generate_site_shared_file(output_filename, top_level_file_callback):
    """Generate site shared file."""
    generate_file(
        output_filename=output_filename,
        top_level_file_callback=top_level_file_callback,
        string_content=r"""
########################################################################
#
# !!!!!! EDIT & CUSTOMIZE THIS FILE !!!!!!
#
########################################################################
#
# Defines build flags common to all the sites. The site specific
# files can override these settings.
# This file is typically included by the site specific site.local file.

# the following are examples of settings. Customize appropriately.
export CC
export CPLUSPLUS
""".lstrip(),
    )


def generate_target_file(output_filename, top_level_file_callback):
    """Generate site local file."""
    generate_file(
        output_filename=output_filename,
        top_level_file_callback=top_level_file_callback,
        string_content=r"""
########################################################################
#
# !!!!!! EDIT & CUSTOMIZE THIS FILE !!!!!!
#
########################################################################
#
# Defines site independent, but target specific build variables
#
# This file is included by overall.mk

CC_DEFINES +=
CC_LIBS +=
""".lstrip(),
    )


def make_children_executable(path, extensions):
    """Make files with certain extensions executable.

    Ignore hidden paths.

    """
    for root, directories, filenames in os.walk(path):
        for d in directories:
            if d.startswith("."):
                directories.remove(d)
        for f in filenames:
            match = False
            for e in extensions:
                match = f.endswith(e)
                if match:
                    break
            if match and not f.startswith("."):
                os.chmod(os.path.join(root, f), 0o755)


_MODULE_MAKEFILE_CONTENTS = """
#------------------------------------------------------------------------------
# DO NOT CHANGE OR MOVE THE LINES BELOW
#
# Include a file that provides much common functionality
# be sure to include this *after* setting the MODULE_* variables
# These lines should be the first thing in the makefile
#------------------------------------------------------------------------------
ifndef YAM_ROOT
    include ../../etc/SiteDefs/mkHome/shared/overall.mk
else
    include $(YAM_ROOT)/etc/SiteDefs/mkHome/shared/overall.mk
endif

#------------------------------------------------------------------------------
# START OF MODULE SPECIFIC CUSTOMIZATION (below)
#------------------------------------------------------------------------------
#
# Uncomment and define the variables as appropriate
#
#------------------------------------------------------------------------------
# Specify any module specific variable definitions here.
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Specify what to build. Libraries should be listed in the PROJ_LIBS
# variable, while binaries go into the PROJ_BINS variable.
#
# If building a library, the name should NOT contain the suffix such
# as ".a" or ".so".
#
# If PROJ_LIBS and PROJ_BINS are left blank, no source files will be
# compiled, but the module may still contain scripts or public header
# files.
#------------------------------------------------------------------------------
# PROJ_LIBS :=
# PROJ_BINS :=
# PROJ_BINS_INTERNAL :=

# FLAVORS-<tgt> :=
# FLAVOR_EXT-<tgt>-<flavor> :=

#------------------------------------------------------------------------------
# Specify public .h, .a, .so, etc. files by filling in *_LINKS variables
# symbolic links to these files get created in top-level directories.
#------------------------------------------------------------------------------
# BIN_LINKS :=
# LIB_MODULE_LINKS :=
# INC_MODULE_LINKS :=
# ETC_MODULE_LINKS :=

#------------------------------------------------------------------------------
# Specify source code to compile (must end in .c, or .cc)
# for source files to be compiled for each PROJ_LIBS and PROJ_BINS
# value listed above.
#------------------------------------------------------------------------------
# CC_SRC-<tgt> :=
# CPLUSPLUS_SRC-<tgt> :=
# F77_SRC-<tgt> :=

#------------------------------------------------------------------------------
# Compilation flags unique to the individual targets.
#------------------------------------------------------------------------------
# CFLAGS-<tgt> :=
# F77FLAGS-<tgt> :=

#------------------------------------------------------------------------------
# When building binary executables and shared libraries, list any extra
# libraries that must be linked in and any -L options needed to find them.
# set the LINKER-<tgt> flag to "$(CPLUPLUS)" to use the C++ linker.
#------------------------------------------------------------------------------
# LIBS-<tgt> :=
# LINKER-<tgt> := $(CPLUSPLUS)

# MODULE_LINKER :=

#------------------------------------------------------------------------------
# Augment flags used when compiling C and C++ source code.
#------------------------------------------------------------------------------
# MODULE_COMPILE_FLAGS :=

#------------------------------------------------------------------------------
# Additional compiler flags to use for dependency information generations
# if left undefined, then all the CFLAGS-<tgt> values are used to set this
# variable.
#------------------------------------------------------------------------------
# MODULE_DEPENDS_FLAGS :=

#------------------------------------------------------------------------------
# Specify information for building Doxygen documentation
# set DOXYGEN_DOCS to "true" to turn on documentation generation
# set DOXYGEN_TAGFILES to other module names for link generation.
#------------------------------------------------------------------------------
# DOXYGEN_DOCS := true
# DOXYGEN_TAGFILES :=

#------------------------------------------------------------------------------
# Add any additional rules specific to the module.
#------------------------------------------------------------------------------

# directory to run regression tests from
# DTEST_TESTDIR := test

#------------------------------------------------------------------------------
# Add module specific clean rule if necessary.
#------------------------------------------------------------------------------
# clean-module::

#------------------------------------------------------------------------------
# END OF MODULE SPECIFIC CUSTOMIZATION (below)
#------------------------------------------------------------------------------
# DO NOT CHANGE OR MOVE THE LINE BELOW
#
# include the "stdrules.mk" file that provides much common functionality.
#------------------------------------------------------------------------------
include $(YAM_ROOT)/etc/SiteDefs/makefile-yam-tail.mk


###########################################################################
# Makefile.yam is the top-level Makefile for the module, and is the one a
# developer should invoke directly to rebuild a single module.
# Invoke it while in the module's checked out src directory.
#
# Makefile.yam - specify source files, public header files and libraries,
#
# This Makefile is used by YAM scripts to build and link a module.
# It should have targets for,
#
#     yam-mklinks links depends libs bins clean
#
# even if some are no-ops.
#
# See http://dartslab.jpl.nasa.gov/cgi/dshell-fom.cgi?file=661
# for more information and Makefile.yam examples
#
# When invoked from the YAM scripts, this Makefile is passed values for
# YAM_NATIVE, YAM_ROOT, YAM_SITE, and YAM_TARGET variables.
#
# Use etc/SiteDefs/Makefile.yam-common to take advantage of some common
# functionality.
#
#     PROJ - What to build. Either the name of a binary executable or a
#     library (in which case $(PROJ) should start with "lib" and NOT contain
#     a suffix such as .a or .so). if left blank, then no source files are
#     compiled. Links for the libraries automatically get exported into the
#     top-level lib/YAM_TARGET, while those for binaries get exported to
#     bin/YAM_TARGET, but the module can contain scripts and header files.
#
#     FLAVORS-<tgt> - List of "flavors" of the module to build for the
#     specified binary/library. If FLAVORS is set to "FOO BAR", then each
#     source file gets compiled twice into the FOO & BAR sub-directories of
#     YAM_TARGET. Libraries and binaries files have "-FOO" or "-BAR" appended
#     to them. The suffix to use can be set by explicitly setting the
#     FLAVOR_EXT-<tgt>-<flavor> to the value of the desired suffix. No suffix
#     is used if the "-NONE-" suffix is specified.
#
#     CC_SRC-<tgt> - list of .c files to compile for the target
#
#     CPLUSPLUS_SRC-<tgt> - list of .cc files to compile for the target
#
#     MODULE_COMPILE_FLAGS - augments standard C preprocessor flags (-I, -D)
#
#     MODULE_DEPENDS_FLAGS - flags to use for dependency information
#
#     LIBS-<tgt> - list of libraries to link in for shared libraries and
#     binary executables for the target
#
#     LINKER-<tgt> - set to "CPLUSPLUS" to use the C++ linker
#
#     CFLAGS-<tgt> - compilation flags specific to the target
#
#     DOXYGEN_DOCS - if "true" then Doxygen docs are generated
#
#     DOXYGEN_TAGFILES - names of other modules to create links for in the
#     Doxygen documentation
#
# The following variables are used by the yam-mklinks and yam-rmlinks rules
# to export and deleted links for the module to the higher level directories.
#
#     BIN_LINKS - will set up links under ../../bin/
#     BIN_MODULE_LINKS - will set up links under ../../bin/<module>/
#
# Additional available variables can be obtained by replacing "BIN" with
# either of "INC", "ETC", "LIB", "BIN", or "DOC"
#
# Additional variables for target specific links are
#
#     BIN_TARGET_LINKS      - will set up links under ../../bin/$(YAM_TARGET)/
#     BIN_sparc-sunos5_LINKS - will set up links under ../../bin/sparc-sunos5/
#
# Additional available variables can be obtained by replacing "BIN" with "LIB"
#
#
# You may also augment the default rules by specifying them in this file.
# Since the "::" versions of the rules are used the effect is to append to
# rather than to replace the default rule.
#
# By default, a module is assumed to be support all the known targets.
# An optional .supported.mk file can be created in the top level module
# directory to restrict the list of supported targets for the module.
# If you need to disable certain targets for this module then create
# a .supported.mk file in the module's directory and add lines so that
# the following variables are set appropriately:
#
#     MODULE_SUPPORTED_TARGETS
#     MODULE_UNSUPPORTED_TARGETS
#     MODULE_SUPPORTED_OS
#     MODULE_UNSUPPORTED_OS
#
# Also an optional .directives.mk file can be created in the top level
# module directory to pass on module specific directives to the site
# configuration files.
""".lstrip()
