: # -*- perl -*-
eval 'exec perl -S $0 ${1+"$@"}'
    if 0;

use File::Copy::Recursive;

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
$yam_root = shift(@ARGV);

# location under YAM_ROOT where the files whould be linked
$dest = shift(@ARGV);

# absolute top level location of the  files to be linked
$rellink = shift(@ARGV);

$cplinks = shift(@ARGV);

$fulldest = ${yam_root} . "/" . ${dest};

# only create the link if there are some files to be linked
mkpath($fulldest,0,0775) if(@ARGV);

foreach $file (@ARGV) {
  @tmp = split("/", $file);
  $filename = pop(@tmp);
  $comp="${fulldest}/" . $filename;
  if (!$cplinks) {
    if  (!-l $comp) {
      print "   linking $file into ./${dest} ...\n";
      symlink(${rellink}. "/" . $file, $comp);
    }
  } else {
      print "   copying $file into ./${dest} ...\n";
      if  (!-e $comp) {
	unlink($comp)
      }
      File::Copy::Recursive::rcopy($file, $comp)
  }
}
