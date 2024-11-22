#!/bin/sh
#
# Creates an overview webpage for the coverage results from lcov and coverage.py.

if [ $# -lt 5 ]
then
    echo "Usage: coverageIndex.sh [src directory] [maintainers] [lcov html directory relative path] [coverage.py html directory relative path] [html output file]"
    exit -1
fi

src_dir="$1"
maintainers_file="$2"
lcov_rel_dir="$3"
covpy_rel_dir="$4"
html_file="$5"
title="Darts Lab Line Coverage Report"

html_output_dir=`dirname "$html_file"`

# Make sure html_file is not a directory.
if [ -d $html_file ]
then
    echo "ERROR: $html_file is a directory. This should be the filename of the html output file."
    exit -1
else
    rm -f "$html_file"
fi

echo "<html><head><title>$title</title></head><body>" >> "$html_file"

font_face="face=Arial,Sans"

echo "<font $font_face size=+2>$title</font><br>" >> "$html_file"
echo "<font $font_face>`date`</font><br><br>" >> "$html_file"

echo "<table><tr>" >> "$html_file"
echo "<td bgcolor=#6688D4><center>&nbsp;<font $font_face color=#FFFFFF size=+1>Module</font>&nbsp;</center></td>" >> "$html_file"
echo "<td bgcolor=#6688D4><center>&nbsp;<font $font_face color=#FFFFFF size=+1>C++ Line Coverage</font>&nbsp;</center></td>" >> "$html_file"
echo "<td bgcolor=#6688D4><center>&nbsp;<font $font_face color=#FFFFFF size=+1>Python Coverage</font>&nbsp;</center></td>" >> "$html_file"
echo "<td bgcolor=#6688D4><center>&nbsp;<font $font_face color=#FFFFFF size=+1>Maintainer</font>&nbsp;</center></td>" >> "$html_file"
echo "</tr>" >> "$html_file"
for module_dir in "$src_dir"/*
do
    module=`basename "$module_dir"`

    lcov_line_message=`lcov --add-trace "$module_dir/lcov.clean.info" |& grep "lines\.\.\." | sed s/lines......:\ // | sed s/\ lines// `
    lcov_int_percent=`echo "$lcov_line_message" | sed "s/..%.*//" `

    covpy_line_message=`grep "<span class='pc_cov'>" "$html_output_dir/$covpy_rel_dir/$module/index.html" | sed "s|.*<span class='pc_cov'>||" | sed "s|</span>.*||"`
    covpy_int_percent=`echo "$covpy_line_message" | sed "s/%.*//" `

    echo "moudle: $module"
    echo "    lcov_line_message: $lcov_line_message"
    echo "    lcov_int_percent: $lcov_int_percent"
    echo "    covpy_line_message: $covpy_line_message"
    echo "    covpy_int_percent: $covpy_int_percent"

    # Print a new row in the table if the module has either C++ or Python coverage results.
    if [ "$lcov_line_message" -o "$covpy_line_message" ]
    then
        echo "<tr>" >> "$html_file"
        echo "<td bgcolor=#DAE7FE>&nbsp;<font ${font_face}>${module}</font>&nbsp;</td>" >> "$html_file"

        if [ "$lcov_line_message" ]
        then
            color="#FF0000"
            if [ "$lcov_int_percent" -ge "15" ]
            then
                color="#FFEA20"
            fi
            if [ "$lcov_int_percent" -ge "50" ]
            then
                color="#A7FC9D"
            fi

            echo "<td bgcolor=${color} align=right>&nbsp;<a href=$lcov_rel_dir/$module/index.html><font ${font_face}>${lcov_line_message}</font></a>&nbsp;</td>" >> "$html_file"
        else
            echo "<td bgcolor=#DAE7FE></td>" >> "$html_file"
        fi

        if [ "$covpy_line_message" ]
        then
            color="#FF0000"
            if [ "$covpy_int_percent" -ge "15" ]
            then
                color="#FFEA20"
            fi
            if [ "$covpy_int_percent" -ge "50" ]
            then
                color="#A7FC9D"
            fi

            echo "<td bgcolor=${color} align=right>&nbsp;<a href=$covpy_rel_dir/$module/index.html><font ${font_face}>${covpy_line_message}</font></a>&nbsp;</td>" >> "$html_file"
        else
            echo "<td bgcolor=#DAE7FE></td>" >> "$html_file"
        fi

        maintainer=`grep $module "$maintainers_file" | sed "s/^ *//" | sed "s/ *= */=/" | grep "^$module=" | sed "s/$module=//"`
        echo "<td bgcolor=#DAE7FE>&nbsp;<font ${font_face}>${maintainer}</font></a>&nbsp;</td>" >> "$html_file"
        echo "</tr>" >> "$html_file"
    else
        echo "<!-- Neither lcov nor coverage.py files were found in $module -->" >> "$html_file"
    fi

done
echo "</table>" >> "$html_file"

# Print the sandbox path.
echo "<br><font $font_face>${src_dir%/*}</font><br>" >> "$html_file"

echo "</body></html>" >> "$html_file"
