"""Check naming convention conformance of scripts."""

import os
import re


def main():
    script_directory = "../../../scripts"
    assert os.path.exists(script_directory)
    for script_name in os.listdir(script_directory):
        if script_name.startswith("."):
            continue

        if not re.match(r"^[a-z\-]+$", script_name):
            print(
                'ERROR: In "{d}", "{n}" should only include lower-case '
                "characters and dashes".format(d=script_directory, n=script_name)
            )


if __name__ == "__main__":
    main()
