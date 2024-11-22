#!/usr/bin/env python
"""Check all Python files for commented out code."""

from __future__ import print_function


def contains_code(input_string):
    code_examples = [
        r"^\s*#*\s*print\s*[\(\'\"].*$",
        r"^\s*#*\s*def\s+[a-zA-Z0-9_]+\(.*$",
        r"^\s*#*\s*class\s+[a-zA-Z0-9_]+.*:\s*$",
        r"^\s*#*\s*if\s+[^:]+ *: *$",
    ]

    for line in input_string.split("\n"):
        for example in code_examples:
            import re

            if re.match(example, line):
                return True
    return False


def main():
    import argparse

    parser = argparse.ArgumentParser("check_for_commented_out_code")
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args()

    failed = False
    for filename in args.filenames:
        file_object = open(filename)
        import tokenize

        g = tokenize.generate_tokens(file_object.readline)
        for token_type, token_value, (start_row, _), _, _ in g:
            import token

            if token_type == token.STRING or token_type == tokenize.COMMENT:
                # If there is a print statement/function in the comment it
                # probably is commented out code.
                if contains_code(token_value):
                    print(
                        'ERROR: Commented out code starting with "{first_few}" found at {filename}:{line_number}'.format(
                            first_few=token_value[: min(len(token_value), 20)],
                            filename=filename,
                            line_number=start_row,
                        )
                    )
                    failed = True

    import sys

    if failed:
        print("Commented out code was found. Delete the code (make use of revision control).")
        sys.exit(10)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
