#!/usr/bin/env python
"""Check that options match naming convention."""

from __future__ import print_function

import argparse
import sys
import token
import tokenize

import enchant


def find_misspelled_word(option_string, enchant_dictionary):
    """Returns the first misspelled word in the option string."""
    for word in option_string.split("-"):
        if word:
            if not enchant_dictionary.check(word):
                return word
    return None


def main():
    parser = argparse.ArgumentParser("check_option_names")
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

    for filename in args.filenames:
        print(filename, file=sys.stderr)
        with open(filename, "r") as file_object:
            g = tokenize.generate_tokens(file_object.readline)
            failed = False
            for token_type, token_value, (start_row, _), _, _ in g:
                if token_type == token.STRING:
                    token_string = eval(token_value, {}, {}).strip()
                    if not token_string.startswith("--") or " " in token_string or "=" in token_string:
                        continue

                    if token_string.lower() != token_string:
                        print(
                            'ERROR: Option "{option}" at '
                            "{filename}:{line_number} should be spelled "
                            "with only lowercase letters".format(
                                option=token_string,
                                filename=filename,
                                line_number=start_row,
                            ),
                            file=sys.stderr,
                        )
                        failed = True
                    else:
                        misspelled_word = find_misspelled_word(
                            option_string=token_string,
                            enchant_dictionary=enchant_dictionary,
                        )
                        if misspelled_word:
                            print(
                                'ERROR: "{word}" in option "{option}" is '
                                "misspelled at "
                                "{filename}:{line_number}".format(
                                    word=misspelled_word,
                                    option=token_string,
                                    filename=filename,
                                    line_number=start_row,
                                ),
                                file=sys.stderr,
                            )
                            failed = True

    if failed:
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
