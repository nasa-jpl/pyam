#!/bin/sh
#
# Creates an overview webpage for the coverage results from dkwstyle and dpylint.

if [ $# -lt 5 ]
then
    echo "Usage: codingstyleIndex.sh [src directory] [maintainers] [dkwstyle html directory relative path] [dpylint html directory relative path] [html output file]"
    exit -1
fi

src_dir="$1"
maintainers_file="$2"
dkwstyle_rel_dir="$3"
dpylint_rel_dir="$4"
html_file="$5"
title="Darts Lab Coding Style Check Report"

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
echo "<td bgcolor=#6688D4><center>&nbsp;<font $font_face color=#FFFFFF size=+1>C++ errors per KLOC</font>&nbsp;</center></td>" >> "$html_file"
echo "<td bgcolor=#6688D4><center>&nbsp;<font $font_face color=#FFFFFF size=+1>Python error rating (out of 10)</font>&nbsp;</center></td>" >> "$html_file"
echo "<td bgcolor=#6688D4><center>&nbsp;<font $font_face color=#FFFFFF size=+1>Maintainer</font>&nbsp;</center></td>" >> "$html_file"
echo "</tr>" >> "$html_file"

for module_dir in "$src_dir"/*
do
    module=`basename "$module_dir"`

    # C++
    file_count=`dkwstyle $module_dir | grep "Processing" | grep -v YamVersion.h | wc --lines`
    if [ "$file_count" -gt "0" ]
    then
        error_count=`dkwstyle $module_dir | grep Error  | wc --lines`
        line_count=`find "$module_dir" \( -name "*.cc" -o -name "*.h" \) | xargs wc -l | tail -1 | sed "s/total//"`
        echo "    Line count:  $line_count"
        errors_per_kloc=`python -c "print('%.2f' % ($error_count*1000./$line_count))"`
        int_errors_per_10kloc=$(($error_count*10000/$line_count))
        echo "    Errors per KLOC:  $errors_per_kloc"
        echo "    Errors per 10 KLOC (integer):  $int_errors_per_10kloc"
    else
        error_count=""
    fi

    # Python
    python_rating=`grep "Your code has been rated at " "$html_output_dir/$dpylint_rel_dir/$module/index.html" | sed "s|.*Your code has been rated at ||" | sed "s|/.*||"`
    if [ "$python_rating" ]
    then
        python_error_rating=`echo "10. - $python_rating" | bc`
        python_error_int_rating=`echo "$python_error_rating / 1" | bc`
    fi

    if [ "$error_count" -o "$python_rating" ]
    then
        echo "<tr>" >> "$html_file"
        echo "<td bgcolor=#DAE7FE>&nbsp;<font ${font_face}>${module}</font>&nbsp;</td>" >> "$html_file"

        # C++ column
        if [ "$error_count" ]
        then
            if [ "$int_errors_per_10kloc" -ge "10" ]
            then
                errors_per_kloc_color="#FF0000"
            elif [ "$int_errors_per_10kloc" -ge "1" ]
            then
                errors_per_kloc_color="#FFEA20"
            else
                errors_per_kloc_color="#A7FC9D"
            fi

            echo "<td bgcolor=${errors_per_kloc_color} align=right>&nbsp;<a href=$dkwstyle_rel_dir/$module/index.html><font ${font_face}>${errors_per_kloc}</font></a>&nbsp;</td>" >> "$html_file"
        else
            echo "<td bgcolor=#DAE7FE></td>" >> "$html_file"
        fi

        # Python column
        if [ "$python_rating" ]
        then
            if [ "$python_error_int_rating" -ge "5" ]
            then
                python_error_rating_color="#FF0000"
            elif [ "$python_error_int_rating" -ge "1" ]
            then
                python_error_rating_color="#FFEA20"
            else
                python_error_rating_color="#A7FC9D"
            fi

            echo "<td bgcolor=${python_error_rating_color} align=right>&nbsp;<a href=$dpylint_rel_dir/$module/index.html><font ${font_face}>${python_error_rating}</font></a>&nbsp;</td>" >> "$html_file"
        else
            echo "<td bgcolor=#DAE7FE></td>" >> "$html_file"
        fi

        # Maintainer column
        maintainer=`grep $module "$maintainers_file" | sed "s/^ *//" | sed "s/ *= */=/" | grep "^$module=" | sed "s/$module=//"`
        echo "<td bgcolor=#DAE7FE>&nbsp;<font ${font_face}>${maintainer}</font></a>&nbsp;</td>" >> "$html_file"

        echo "</tr>" >> "$html_file"
    else
        echo "<!-- Neither dkwstyle nor dpylint_rel_dir files were found for module $module -->" >> "$html_file"
    fi
done
echo "</table>" >> "$html_file"

# Print the sandbox path.
echo "<br><font $font_face>${src_dir%/*}</font><br>" >> "$html_file"

echo "</body></html>" >> "$html_file"
