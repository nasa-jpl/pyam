#!/bin/sh -x
#
# Builds a overview HTML page for the cppcheck html reports.
#
# Not necessary, but cppcheck-htmlreport.patch in this directory is a patch to
# make cppcheck-htmlreport make errors more visibile by coloring them red.

if [ $# -lt 3 ]
then
    echo "Usage: cppcheckIndex.sh [src directory] [maintainers] [html output file]"
    exit -1
fi

src_dir="$1"
maintainers_file="$2"
html_file="$3"
title="Darts Lab Static Code Analysis Report"

rm -f "$html_file"

echo "<html><head><title>$title</title></head><body>" >> "$html_file"

font_face="face=Arial,Sans"

echo "<font $font_face size=+2>$title</font><br>" >> "$html_file"
echo "<font $font_face>`date`</font><br><br>" >> "$html_file"

echo "<table><tr>" >> "$html_file"
echo "<td bgcolor=#6688D4><center>&nbsp;<font $font_face color=#FFFFFF size=+1>Module</font>&nbsp;</center></td>" >> "$html_file"
echo "<td bgcolor=#6688D4><center>&nbsp;<font $font_face color=#FFFFFF size=+1>Errors per KLOC</font>&nbsp;</center></td>" >> "$html_file"
echo "<td bgcolor=#6688D4><center>&nbsp;<font $font_face color=#FFFFFF size=+1>Critical Errors</font>&nbsp;</center></td>" >> "$html_file"
echo "<td bgcolor=#6688D4><center>&nbsp;<font $font_face color=#FFFFFF size=+1>Maintainer</font>&nbsp;</center></td>" >> "$html_file"
echo "</tr>" >> "$html_file"

for module_dir in "$src_dir"/*
do
    module=`basename "$module_dir"`
    file_count=`find "$module_dir" -name "*.cc" | grep -v YamVersion.h | wc --lines`

    echo "$module $file_count"

    if [ "$file_count" -gt "0" ]
    then
        error_count=`grep "<error" "$module_dir/cppcheck.xml" | wc --lines`
        line_count=`find "$module_dir" \( -name "*.cc" -o -name "*.h" \) | xargs wc -l | tail -1 | sed "s/total//"`
        echo "    Line count:  $line_count"
        errors_per_kloc=`python -c "print('%.2f' % ($error_count*1000./$line_count))"`
        int_errors_per_10kloc=$(($error_count*10000/$line_count))
        echo "    Errors per KLOC:  $errors_per_kloc"
        echo "    Errors per 10 KLOC (integer):  $int_errors_per_10kloc"
        if [ "$int_errors_per_10kloc" -ge "10" ]
        then
            errors_per_kloc_color="#FF0000"
        elif [ "$int_errors_per_10kloc" -ge "1" ]
        then
            errors_per_kloc_color="#FFEA20"
        else
            errors_per_kloc_color="#A7FC9D"
        fi

        critical_error_count=`grep "<error" "$module_dir/cppcheck.xml" | grep severity=\"error\" | wc --lines`
        echo "    Critical error count: $critical_error_count"
        if [ "$critical_error_count" -ge "1" ]
        then
            critical_error_count_color="#FF0000"
        else
            critical_error_count_color="#A7FC9D"
        fi

        maintainer=`grep $module "$maintainers_file" | sed "s/^ *//" | sed "s/ *= */=/" | grep "^$module=" | sed "s/$module=//"`

        echo "<tr>" >> "$html_file"
        echo "<td bgcolor=#DAE7FE>&nbsp;<a href=$module/index.html><font ${font_face}>${module}</font></a>&nbsp;</td>" >> "$html_file"
        echo "<td bgcolor=${errors_per_kloc_color} align=right>&nbsp;<font ${font_face}>${errors_per_kloc}</font>&nbsp;</td>" >> "$html_file"
        echo "<td bgcolor=${critical_error_count_color} align=right>&nbsp;<font ${font_face}>${critical_error_count}</font>&nbsp;</td>" >> "$html_file"
        echo "<td bgcolor=#DAE7FE>&nbsp;<font ${font_face}>${maintainer}</font></a>&nbsp;</td>" >> "$html_file"
        echo "</tr>" >> "$html_file"
    else
        echo "<!-- No .cc files were found in $module -->" >> "$html_file"
    fi
done
echo "</table>" >> "$html_file"

# Print the sandbox path.
echo "<br><font $font_face>${src_dir%/*}</font><br>" >> "$html_file"

echo "</body></html>" >> "$html_file"
