#!/usr/bin/env python
"""Find use of a given keyword."""

from __future__ import print_function


def main():
    import argparse

    parser = argparse.ArgumentParser("find_token.py")
    parser.add_argument("--keyword", action="store_true", help="only search for keywords")
    parser.add_argument("--name", action="store_true", help="only search for names")
    parser.add_argument(
        "--word",
        action="store_true",
        help="only search for words that are part of strings",
    )
    parser.add_argument("token", help="the token to search for")
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args()

    import keyword
    import sys

    if args.keyword and not keyword.iskeyword(args.token):
        print('ERROR: "{word}" is not a keyword in Python'.format(word=args.token))
        sys.exit(1)

    if not (args.keyword ^ args.name ^ args.word):
        print("ERROR: Only one option (keyword, name, or word) can be used")
        sys.exit(1)

    if args.word and len(args.token.split()) > 1:
        print('ERROR: "{token}" is not a word as it contains whitespace'.format(token=args.token))
        sys.exit(1)

    found = False
    for filename in args.filenames:
        file_object = open(filename)
        import tokenize

        g = tokenize.generate_tokens(file_object.readline)
        for token_type, token_value, (start_row, _), _, line in g:
            import token

            if (args.keyword or args.name) and token_type == token.NAME and token_value == args.token:
                found = True
            elif args.word and token_type == token.STRING:
                for word in token_value.strip("'\"").split():
                    if args.token == word:
                        found = True
            elif token_value == args.token:
                found = True

            if found:
                print(line.strip("\n"))
                break

    if found:
        sys.exit(0)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
