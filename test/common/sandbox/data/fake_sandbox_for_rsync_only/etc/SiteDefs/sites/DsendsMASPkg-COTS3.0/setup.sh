setenv DSENDS_ROOT /nav/common/sw/linux/redhat/8.0/Dsends/COTS3.0/tmp/DsendsMASBasePkg-R3-00b
setenv DSENDS_BASE_PKG /nav/common/sw/linux/redhat/8.0/Dsends/COTS3.0/tmp/DsendsMASBasePkg-R3-00b
setenv COTS_PATH /group/monte/tools/rhe4/core-3.0
setenv COTS_PYTHONVER python2.6
setenv COTS_PYTHONPATH /group/monte/tools/rhe4/core-3.0/lib/python2.6/site-packages
setenv DTPS_PATH /nav/common/sw/linux/redhat/8.0/Dsends/COTS3.0/EXP/DTPS/DTPS-3.00
setenv PERL5LIB $DTPS_PATH/perl
setenv HDF5_PATH $DTPS_PATH/hdf5-1.8.1/build
setenv CSPICE_PATH $DTPS_PATH/cspice-v62-32bit
setenv MATLAB_LIB_PATH /nav/common/sw/linux/redhat/8.0/matlab/14.2/bin/glnx86
setenv MATLAB_BINDIR /usr/local/bin
# setenv MAS_LOAD_POINT /nav/common/sw/linux/redhat/rhel4/cots/core3.0/masl
setenv MASL_LIB_PATH /nav/common/sw/linux/redhat/rhel4/cots/core3.0/masl/current/lib
source $DSENDS_ROOT/src/SiteDefs/sites/DsendsMASPkg-COTS3.0/site-setup.sh
alias myDrun $DSENDS_ROOT/bin/Drun
alias ymk 'gmake -f Makefile.yam'
