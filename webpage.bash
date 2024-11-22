#!/bin/bash -ex
#
# Update the webpage: https://dartslab.jpl.nasa.gov/internal/www/pyam/

if [ $# -eq 0 ]
then
    readonly RAW_OUTPUT_DIRECTORY='/home/dlab3/FROM-DLAB/repo/www/pyam'
elif [ $# -eq 1 ]
then
    readonly RAW_OUTPUT_DIRECTORY="$1"
else
    echo 'Usage: ./webpage.bash <output_directory>'
    exit 1
fi

# Get absolute path
readonly OUTPUT_DIRECTORY=$(readlink -f "$RAW_OUTPUT_DIRECTORY")

# Change directory so that we are in the root of pyam
readonly RESOLVED_FILE_PATH=$(readlink -f "$0")
readonly PYAM_DIRECTORY_PATH=$(dirname "$RESOLVED_FILE_PATH")
cd "$PYAM_DIRECTORY_PATH"

version=$(./pyam --version 2>&1 | sed -e 's/pyam //')

if [ ! -d "$OUTPUT_DIRECTORY" ]
then
    mkdir "$OUTPUT_DIRECTORY"
fi

readonly TEMPORARY_RST="$OUTPUT_DIRECTORY/index.rst"
cat 'webpage/main.rst' > "$TEMPORARY_RST"
echo -e '\n' >> "$TEMPORARY_RST"
cat 'HISTORY.rst' >> "$TEMPORARY_RST"
rst2html --strict --stylesheet='webpage/bootstrap.css' "$TEMPORARY_RST" "$OUTPUT_DIRECTORY/index.html"
rm -f "$TEMPORARY_RST"

rst2pdf 'README.rst' --output="$OUTPUT_DIRECTORY/README.pdf"
rst2html --strict --stylesheet='webpage/bootstrap.css' 'README.rst' "$OUTPUT_DIRECTORY/README.html"

./distribute.bash "$OUTPUT_DIRECTORY"

# Point to the latest tarball on the webpage itself.
cd "$OUTPUT_DIRECTORY"
sed --in-place='' "s/pyam.tar.gz/pyam-$version.tar.gz/g" 'index.html'

# Check all URLs except for flaky tigris.
linkchecker \
    --config="$PYAM_DIRECTORY_PATH/.linkcheckerrc" \
    --ignore-url='http://pysvn.tigris.org/' \
    "file://$OUTPUT_DIRECTORY/index.html"
