#!/usr/bin/env python
"""Spell check strings and comments in Python code."""

from __future__ import print_function

import argparse
import re
import sys
import token
import tokenize

import enchant


NORMALIZE_REGEX = re.compile("([a-z])([A-Z][a-z])")


def normalize(line):
    """Normalize camel-cased words."""
    return NORMALIZE_REGEX.sub(r"\1 \2", line)


def main():
    parser = argparse.ArgumentParser("check_spelling")
    parser.add_argument(
        "--word-list",
        "-s",
        default=None,
        required=False,
        help="extend the default word list with contents of this file",
    )
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args()

    if args.word_list:
        enchant_dictionary = enchant.DictWithPWL("en_US", args.word_list)
    else:
        enchant_dictionary = enchant.Dict("en_US")

    failed = False
    for filename in args.filenames:
        with open(filename, "r") as file_object:
            file_object = open(filename)
            g = tokenize.generate_tokens(file_object.readline)
            for token_type, token_value, (start_row, _), _, _ in g:
                if token_type == token.STRING:
                    check_string = eval(token_value, {}, {})
                elif token_type == tokenize.COMMENT:
                    check_string = token_value.replace("#", "", 1)
                else:
                    continue

                for word in normalize(check_string).split():
                    if word.startswith("--"):
                        continue
                    word = word.strip(" .")
                    if re.match(r"^[a-zA-Z\-]+$", word):
                        if not enchant_dictionary.check(word):
                            print(
                                'ERROR: "{word}" is misspelled at {filename}:{line_number}'.format(
                                    word=word,
                                    filename=filename,
                                    line_number=start_row,
                                )
                            )
                            failed = True

    if failed:
        sys.exit(10)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
