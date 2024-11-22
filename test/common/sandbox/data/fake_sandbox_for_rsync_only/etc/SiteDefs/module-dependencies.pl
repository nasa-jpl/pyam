: # -*- perl -*-
eval 'exec perl -S $0 ${1+"$@"}'
    if 0;

use strict;
use FileHandle;
use File::Find;
use File::Basename;
use File::PathConvert;
use Cwd;
use DSubUtils;
use Data::Dumper;

my $program = substr($0,rindex($0,"/")+1);

my($test);
my($outfile);
while ($test = shift(@ARGV)) {
  #  print "test = <$test>\n";
  if ($test eq '-h' || $test eq '-H' || $test eq '-help') {
    &usage;
  } elsif ($test eq '-outfile') {
    $outfile = shift;
  } else {
    print "Unrecognized option: '$test'";
    &usage;
  }
}

if (!$outfile) {
  $outfile = "../allDEP";
}

my $yam_root = $ENV{YAM_ROOT};
my $modname = $ENV{MODULE_NAME};
my $yam_target = $ENV{YAM_NATIVE};
#my $fh;


my @mfiles;
# if (-r "$yam_root/src/$modname/$yam_target") {
#   opendir(DIR, "$yam_root/src/$modname/$yam_target") || die "Cannot read $yam_root/src/$modname/$yam_target directory";
#   my @afiles = readdir(DIR);
#   @mfiles = grep(/(.*)\.d/, @afiles);
# #print "mfile=", @mfiles, " afiles=", @afiles;;
#   close(DIR);
# }

my @mfiles = <$yam_root/src/$modname/$yam_target/*.d $yam_root/src/$modname/$yam_target/*/*.d>;
#print "fls=@mfiles\n";
#exit(0);


if (!@mfiles) {
  print "\n  ****  Skipping module - $modname ******\n\n";
  open (DEPOUT, ">> $yam_root/src/nDEP") || die "Cannot write to $yam_root/src/nDEP";
  print DEPOUT "$modname=", "==================", "\n";
  close DEPOUT;
  exit(0);
}

my @modfiles;
my %deps;
my $line;
my $currfile;
my $depfile;
my $depmod;
my @dependencies;

foreach my $mfile (@mfiles) {
  open(DEP, "< $mfile") || die "Cannot read $mfile file";
  while ($line = <DEP>) {
    # see if have a new object file
    if ($line =~ m@^(.*)\.o@) {
      $currfile = $1;
      #    print "currfile=$currfile\n";
      next;
    }
    chop($line);

    # is this a module internal file, then skip and continue
    next if ($line !~ m@^\s*/@);

    # do we have a dependency pointing directly into src/???
    # This is no-no. Pring a warning.
    my $pat = DSubUtils::string2pattern($modname);
    if ($line =~ m@$yam_root/src/$pat/@) {
      print "$mfile: path into src/ - $line\n";
      next;
    }

    # seem to have found an external include file. Process it
    $line =~ s/\\//;		# get rid of the trailing backslash

    #  $line =~ s/\s//g;	# get rid of all white space
    my @files = split(" ", $line);

    foreach my $file (@files) {
      # get the real path to the file
      my $cdir = File::PathConvert::realpath($file);

      # check if the file is within the module - something is fishy
      if ($cdir =~ m@$yam_root/src/$pat/@) {
	print "\n$mfile: file within module: $file\n";
	next;
      }

      # check if file is within a work module - something is fishy
      #  if ($file =~ m@$yam_root/include/([^/]*)/(.*)@) {
      if ($cdir =~ m@$yam_root/src/([^/]*)/(.*)@) {
	$depmod = $1;
	$depfile = $2;
	#      if ($depfile eq "YamVersion.h") {
	#      }
	if ($depmod eq $modname) {
	  print "\n!!!!!!!! self, $depfile, $file, $cdir\n\n";
	  next;
	} else {
	  push(@dependencies, [$depmod, $depfile]);
	}
	$deps{$depmod} = 1;
      } elsif ($cdir =~ m @$ENV{YAM_VERSIONS}/([^/]*)/([^/]*)-R([^/]*)/(.*)@) {
	$depmod = $1;
	if ($depmod ne $2) {
	  print "WARNING: Something fishy with link module - $file, cdir=$cdir\n";
	  next;
	}
	my $depmodrev = $3;
	$depfile = $4;
	if ($depmod eq $modname) {
	  print "\n!!!!!!!! self, $depfile, $file, $cdir\n\n";
	  next;
	} else {
	  push(@dependencies, [$depmod, $depfile]);
	}
	$deps{$depmod} = 1;
      } else {
	print "Skipping external file - $file, cdir=$cdir\n";
      }
    }
    #  printf "   %10s - %s\n", $depmod, $depfile;
  }
  close(DEP);
}

my $udeps;
map {$udeps->{$_->[0]}->{$_->[1]} = 1} @dependencies;

#my @uniqdeps = DSubUtils::arrayUniquify(@dependencies);
#@uniqdeps = sort @uniqdeps;


# open (DEPOUT, ">> $yam_root/src/nDEP") || die "Cannot write to $yam_root/src/nDEP";
# print DEPOUT "$modname=", join(",", sort(keys %deps)), "\n";
# close DEPOUT;


#print "uniqdeps = ", join(", ", @uniqdeps);
#foreach my $dmod (sort keys %$udeps) {
#  print "  $dmod:\n";
#  foreach my $dfile (sort keys %{$udeps->{$dmod}}) {
#    print "  \t\t$dfile\n";
#  }
#}

my $fdeps;
foreach my $dmod (keys %$udeps) {
  foreach my $dfile (keys %{$udeps->{$dmod}}) {
    push(@{$fdeps->{$dmod}}, $dfile);
  }
}

#print Data::Dumper->Dump([$fdeps], ["vals{$modname}"]);

#print "outfile=$outfile";
open (DEPOUT, ">> $outfile") || die "Cannot write to $outfile";
print DEPOUT "# \"$modname\" module in $yam_root\n";
print DEPOUT Data::Dumper->Dump([$fdeps], ["moddeps{\'$modname\'}"]);
print DEPOUT "\n1;\n";
close DEPOUT;

sub usage {
  print STDERR "\nusage: $program [-h] [-outfile file]\n";
  exit(2);
}
