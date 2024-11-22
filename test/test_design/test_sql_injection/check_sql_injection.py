#!/usr/bin/env python
"""Checks for possible SQL injection."""

from __future__ import print_function


def has_sql_statement(string):
    """Returns the first misspelled word in the option string."""
    for sql_keyword in [
        "SELECT",
        "INSERT" "UPDATE" "DELETE" "CREATE" "DROP" "ALTER" "INDEX",
    ]:
        for word in string.split():
            if sql_keyword == word.strip().strip('"').strip("'"):
                return True
    return False


def main():
    import argparse

    parser = argparse.ArgumentParser("check_sql_injection")
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args()

    failed = False
    import sys

    for filename in args.filenames:
        with open(filename, "r") as file_object:
            import tokenize

            g = tokenize.generate_tokens(file_object.readline)
            for token_type, token_value, (start_row, _), _, _ in g:
                import token

                if token_type == token.STRING and has_sql_statement(token_value):
                    if "'%s'" in token_value or '"%s"' in token_value:
                        print(
                            'ERROR: Quoted "%s" on line {line_number} indicates'.format(line_number=start_row)
                            + " that you are trying do some sort of string concatenate, which risks SQL injection."
                            + " Use parameterized statements instead."
                        )
                        failed = True

    if failed:
        sys.exit(10)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
