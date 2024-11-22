""""Contains LocalFileSystem class."""

from __future__ import absolute_import

import locale
import os
import shutil
import stat
import subprocess
import tempfile

from . import file_system
from . import yam_log


class LocalFileSystem(file_system.FileSystem):
    """Local implementation of file_system."""

    @yam_log.function_logger("make_read_only")
    def make_read_only(self, filename):
        """Implementation of file_system.make_read_only()."""
        # Don't make files read-only as that makes "rm -r" annoying.
        if os.path.isdir(filename):
            return

        try:
            # Note that Linux has no os.lchmod()
            if not stat.S_ISLNK(os.lstat(filename).st_mode):
                os.chmod(filename, (0o111 if executable(filename) else 0) | 0o444)
        except OSError:
            pass

    @yam_log.function_logger("make_read_only_recursively")
    def make_read_only_recursively(self, directory):
        """Implementation of file_system.make_read_only_recursively()."""
        for root, _, files in os.walk(directory):
            for name in files:
                full_path = os.path.join(root, name)
                self.make_read_only(full_path)

    @yam_log.function_logger("make_writable")
    def make_writable(self, filename):
        """Implementation of file_system.make_writable()."""
        try:
            # Note that Linux has no os.lchmod()
            if not stat.S_ISLNK(os.lstat(filename).st_mode):
                os.chmod(filename, (0o111 if executable(filename) else 0) | 0o664)
        except OSError:
            pass

    @yam_log.function_logger("path_exists")
    def path_exists(self, path):
        """Local implementation of file_system.path_exists()."""
        return os.path.exists(path)

    @yam_log.function_logger("list_directory")
    def list_directory(self, path):
        """Local implementation of file_system.list_directory()."""
        try:
            return os.listdir(path)
        except OSError:
            return []

    @yam_log.function_logger("make_directory")
    def make_directory(self, path):
        """Local implementation of file_system.make_directory()."""
        try:
            os.makedirs(path)
        except OSError:
            pass

    @yam_log.function_logger("remove_directory")
    def remove_directory(self, path):
        """Local implementation of file_system.remove_directory()."""
        # Move into a sibling directory first in case some files cannot be
        # deleted.
        temporary_directory = tempfile.mkdtemp(dir=os.path.dirname(path))

        new_path = os.path.join(temporary_directory, os.path.basename(path))

        os.rename(path, new_path)
        del path

        shutil.rmtree(temporary_directory, ignore_errors=True)

    @yam_log.function_logger("move")
    def move(self, source_path, destination_path, progress_callback=lambda _: None):
        """Local implementation of file_system.move()."""
        # Move into a sibling directory first in case some files cannot be
        # deleted (when moving to a separate file system).
        temporary_directory = tempfile.mkdtemp(dir=os.path.dirname(source_path))

        new_source_path = os.path.join(temporary_directory, os.path.basename(source_path))

        os.rename(source_path, new_source_path)
        del source_path

        # shutil.move() will copy if it cannot just rename.
        # Ignore errors about not being able to remove source path.
        try:
            shutil.move(src=new_source_path, dst=destination_path)
        except (OSError, shutil.Error) as exception:
            progress_callback(str(exception))

        shutil.rmtree(temporary_directory, ignore_errors=True)

    @yam_log.function_logger("symbolic_link")
    def symbolic_link(self, source, link_name, progress_callback=lambda _: None):
        """Local implementation of file_system.symbolic_link()."""
        try:
            if os.path.islink(link_name):
                os.remove(link_name)

            os.symlink(source, link_name)
        except OSError as exception:
            progress_callback(str(exception))

    @yam_log.function_logger("write_to_file")
    def write_to_file(self, string_data, filename):
        """Local implementation of file_system.write_to_file()."""
        with open(filename, "w") as f:
            f.write(string_data)

    @yam_log.function_logger("read_file")
    def read_file(self, filename):
        """Local implementation of file_system.read_file()."""
        with open(filename, "r") as f:
            return f.read()

    @yam_log.function_logger("find_dangling_links")
    def find_dangling_links(self, path):
        """Local implementation of file_system.find_dangling_links()."""

        @yam_log.function_logger("filter_non_existent")
        def filter_non_existent(filename_list, root):
            """Return list of non-existent file."""
            non_existent_list = []
            for f in filename_list:
                path = os.path.join(root, f)
                if not os.path.exists(os.path.join(root, f)):
                    non_existent_list.append(path)
            return non_existent_list

        dangling_links = []
        for root, dirs, filenames in os.walk(path):
            dangling_links += filter_non_existent(dirs, root) + filter_non_existent(filenames, root)
        return dangling_links

    @yam_log.function_logger("common_prefix")
    def common_prefix(self, path_list):
        """Local implementation of file_system.common_prefix()."""
        return os.path.commonprefix(path_list)

    @yam_log.function_logger("resolve_path")
    def resolve_path(self, path):
        """Local implementation of file_system.resolve_path()."""
        try:
            return os.path.realpath(path)
        except OSError:  # pragma: NO COVER
            # This only happens if the link gets removed during the call to
            # os.path.realpath()
            return path  # pragma: NO COVER

    @yam_log.function_logger("create_temporary_directory")
    def create_temporary_directory(self):
        """Local implementation of file_system.temporaryDirectory()."""
        fname = tempfile.mkdtemp()
        # make the release directory readable
        os.chmod(fname, 0o755)
        return fname

    @yam_log.function_logger("execute")
    def execute(self, filename, working_directory):
        """Local implementation of file_system.execute()."""
        p = subprocess.Popen(
            [filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=working_directory,
        )
        (output, error) = p.communicate()

        encoding = locale.getpreferredencoding(False)
        return (p.returncode, output.decode(encoding), error.decode(encoding))


def executable(filename):
    """Return True if file is executable by owner."""
    return stat.S_IMODE(os.lstat(filename).st_mode) & 0o100
