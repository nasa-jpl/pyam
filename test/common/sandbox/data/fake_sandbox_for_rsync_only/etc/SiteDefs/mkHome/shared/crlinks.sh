#! /bin/sh

# this script is used for the yam-mklinks Makefile.yam target to export
# module links to the top level
#
# USAGE:
#     crlinks.sh $YAM_ROOT $destdir $moduledir file1 file2 ....
#
#  destdir - is the relative path below YAM_ROOT where the links
#    should be created
#  moduledir - is the path to the module. Its value depends on whether
#    the module is a link or a work module.

# value of YAM_ROOT
yam_root=$1
shift

# location under YAM_ROOT where the files whould be linked
dest=$1
shift

# absolute top level location of the  files to be linked
rellink=$1
shift

#cmd1="echo $dest | sed 's@${yam_root}/@@"
#subpath1=./`eval $cmd1`
#subpath=`echo $dest | sed 's@${yam_root}@@`

fulldest=${yam_root}/${dest}

# only create the link if there are some files to be linked
if [ "$#" != "0" ]; then
  mkdir -p $fulldest
fi


while [ "$#" != "0" ]; do
  file=$1
  shift
  comp=`basename $file`
  if [ ! -h ${fulldest}/$comp ]; then
     echo "   linking $file into ./${dest} ...";
     ln -s ${rellink}/$file ${fulldest}/$comp;
  fi;
done
