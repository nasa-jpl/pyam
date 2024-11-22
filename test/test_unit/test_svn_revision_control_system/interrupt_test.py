"""Test to confirm that we can SIGINT can interrupt SVN progress.

By default PySVN doesn't properly cancel on SIGINT. We had to add a
callback to enable this.

"""

try:
    raw_input
except NameError:
    # Python 3.
    raw_input = input  # pylint: disable=W0622


def main():
    from yam import svn_revision_control_system

    svn_revision_control_system = svn_revision_control_system.SVNRevisionControlSystem(
        username=None,
        login_callback=lambda realm, username, may_save: (0, "", "", False),
        trust_ssl_server_callback=lambda trust_dict: (False, 0, False),
        progress_callback=lambda current_bytes=-1, print_time_last=None: None,
    )

    # Create a temporary directory and create an repository in it
    import tempfile

    temporary_file_path = tempfile.mkdtemp()

    import subprocess
    import os

    relative_repository_path = os.path.join(temporary_file_path, "temporary_repository")
    subprocess.call(["svnadmin", "create", relative_repository_path])

    repository_url = "file://" + os.path.abspath(path=relative_repository_path)

    check_out_directory = os.path.join(temporary_file_path, "checkout_test")
    svn_revision_control_system.check_out(source=repository_url, target=check_out_directory)

    for i in range(100):
        filename = os.path.join(check_out_directory, str(i))
        with open(filename, "w") as f:
            f.write(1000 * "blah")
        svn_revision_control_system.add_file(filename)

    # Wait until parent process wants us to check in files
    print("waiting")
    raw_input()

    import sys

    try:
        svn_revision_control_system.check_in(path=check_out_directory, log_message="")
        print("ERROR: No KeyboardInterrupt")
        sys.exit(2)
    except KeyboardInterrupt:
        print("OK: KeyboardInterrupt")
        import shutil

        shutil.rmtree(path=temporary_file_path, ignore_errors=True)
        sys.exit(0)


if __name__ == "__main__":
    main()
