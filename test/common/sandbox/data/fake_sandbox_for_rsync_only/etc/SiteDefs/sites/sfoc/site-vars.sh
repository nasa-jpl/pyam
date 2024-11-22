# site specific environment variables

ETS=/TPS/V12.1
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${ETS}/lib:/dsw/gcc-3.1/lib:/dsw/gcc-3.1/lib/sparcv9
#export LD_LIBRARY_PATH

# need to run-time load the shared libraries
TK_PKGLIBRARY=${ETS}/lib/libtk8.3.so
TIX_PKGLIBRARY=${ETS}/lib/libtix8.2.so
export TK_PKGLIBRARY
export TIX_PKGLIBRARY

# need to run-time init.tcl files
TK_LIBRARY=${ETS}/lib/tk8.3
export TK_LIBRARY
TIX_LIBRARY=${ETS}/lib/tix8.2
export TIX_LIBRARY
