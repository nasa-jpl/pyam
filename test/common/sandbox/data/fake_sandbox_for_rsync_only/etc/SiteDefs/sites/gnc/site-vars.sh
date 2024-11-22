# site specific environment variables

if [ "$YAM_TARGET" = "sparc-sunos5.9" ]; then
    # GRAPHVIZ_VERSION=1.9
    # GRAPHVIZ_LIBDIR=/usr/lib/graphviz

    # for TCL
    TCL_VERSION=8.0
    TCL_LIBDIR=/dsw/gca-local/lib
    export TCL_VERSION
    export TCL_LIBDIR

    TCLSQL_LIBDIR=/home/atbe/pkgs/src/tcl-sql/tcl-sql-200000114
    export TCLSQL_LIBDIR

    # for the dom & XML packages
    TCLLIBPATH="${TCLLIBPATH}  /home/atbe/pkgs/lib"
    export TCLLIBPATH

    # for TK
    TK_VERSION=8.0
    export TK_VERSION

    TK_VERSION=8.4
    TK_PKGLIBRARY=/home/atbe/pkgs/${YAM_TARGET}/lib/libtk8.4.so
    TK_LIBRARY=/dsw/gca-local/lib/tk8.4

    # TK_LIBRARY=/home/atbe/pkgs/${YAM_NATIVE}/stow/tk8.4.4/lib/tk8.4
    # TCLGTK_LIBDIR=/home/atbe/pkgs/i486-rh9-linux/stow/tcl-gtk-0.07/lib/tcl-gtk
    export TK_LIBRARY
    export TCLGTK_LIBDIR
    export TK_PKGLIBRARY

    # export POVRAY_BIN=/usr/local/bin/povray

    GNOCL_VERSION=0.5.14
    export GNOCL_VERSION
	if  [ "X$GNOCL_LIBDIR" = "X" ]; then
		# GNOCL_LIBDIR=/home/atbe/pkgs/src/gtk/gnocl-0.5.14-rh9-linux/src
                # GNOCL_LIBDIR=/home/atbe/pkgs/src/gtk/gnocl-0.5.14-sparc-sunos5.9/src
                # GNOCL_LIBDIR=/home/mslgnc/rover/sparc-sunos5.9/lib/gnocl-0.5.14
		GNOCL_LIBDIR=/home/atbe/pkgs/src/gtk/gnocl-0.5.17-sparc-sunos5.9/src
		export GNOCL_LIBDIR
	fi
fi
