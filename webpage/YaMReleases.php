
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
    <script src="https://cdn.jsdelivr.net/npm/jquery@3.6.3/dist/jquery.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js"></script>
    <link href="https://cdn.datatables.net/v/dt/dt-1.13.2/datatables.min.css"/>
    <script src="https://cdn.datatables.net/v/dt/dt-1.13.2/datatables.min.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js"></script>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" />
    <script src="//code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
    <link rel="stylesheet" href="//code.jquery.com/ui/1.11.4/themes/smoothness/jquery-ui.css">
    <link rel="icon" type="image/x-icon" href="/dlab-logo.png?">
    <title>YaM Releases</title>
</head>
<body bgcolor=LightSeaGreen>
<!-- Commenting out this line as it yeilds a high risk error in code checks. Uncomment at your own risk:
# <form name="form" id="form" action="<?php echo($_SERVER['PHP_SELF']) ?>" method="POST">
-->
<div style="clear:both"></div>
<br />
<?php
#=====================================
# CUSTOMIZE FOR YAM PROJECT
$title = "<font size=2 style=\"padding:12px\"><a href=https://dartslab.jpl.nasa.gov/References/pdf/2006-yam-smcit.pdf>YaM</a> Concurrent Software Development Toolkit, DARTS Lab, Jet Propulsion Laboratory/California Institute of Technology</font>";
$title .= "<h2 style=\"padding:12px, padding-top:-40px;\">Darts Lab YaM Releases</h2>";

# name of the YaM project
$project = "Dshell";

# $changelogDir_url - The URL that points to the directory containing
#        the module/package release ChangeLog etc. files
# $changelogDir_url = "";

# $bugEntry_url - The URL pointing to the bug entry for a specific bug id
# $bugEntry_url = "";

# ChangeLogs links filesystem path
$changelogs_path = "/home/dlab3/FROM-DLAB/repo/www/YAM_WWW/YaMDshell/READMES_DIR";

# connection parameters for the YaM MySQL database
$mysqlPort = "localhost.localdomain:3306";
$mysqlPort = "dartslab.jpl.nasa.gov";
# $mysqlUser = "";
$mysqlPassword = "PASSWORD GOES HERE";

# connection parameters for the YaM MySQL database
$bugzillaPort = "dartslab.jpl.nasa.gov";
# $bugzillaUser = "";
$bugzillaPassword = "";
$bugsdesc = "";
$bugsdata = "";

#=====================================
# DO NOT MODIFY BELOW THIS LINE
#

# reverse the sort order
function flipSortDir ($mysortDir) {
  if ($mysortDir == "DESC") {
     $str = "ASC";
  } else if ($mysortDir == "ASC") {
     $str = "DESC";
  }
  return $str;
}



function pagination ($page, $limit, $totalrows, $url) {
    if(empty($page)){
        $page = 1;
    }

    $limitvalue = $page * $limit - ($limit);
    $str = "";
    if($page != 1){
        $pageprev = $page-1;
        $str .= "<a href=\"$url&page=$pageprev\">PREV".$limit."</a>&nbsp;\n";
    }else{
        $str .= "<b>PREV".$limit."</b>&nbsp;\n";
    }

    $numofpages = $totalrows / $limit;

    for($i = 1; $i <= $numofpages; $i++){
        if($i == $page){
            $str .= "<b>" . $i."&nbsp;</b>\n";
        }else{
            $str .= "<a href=\"$url&page=$i\">$i</a>&nbsp;\n";
        }
    }
    if(($totalrows % $limit) != 0){
        if($i == $page){
            $str .= "<b>" . $i."&nbsp;</b>";
        }else{
            $str .= "<a href=\"$url&page=$i\">$i</a>&nbsp;\n";
        }
    }
    if(($totalrows - ($limit * $page)) > 0){
        $pagenext = $page+1;

        $str .= "<a href=\"$url&page=$pagenext\">NEXT".$limit."</a>\n";
    }else{
        $str .= "<b>NEXT".$limit . "\n</b>";
    }
   return $str;
 }


 /*
  * Returns a string with imploded array-elements like ?key1=value1&key2=value2
  * if array is empty or no array, it will return an empty string
  */
function httpimplode($aryInput, $quma = true) {
     if (is_array($aryInput) && count($aryInput)>0) {
         if ($quma == true) {
             $result = '?';
         } else {
             $result = '';
         }
         foreach ($aryInput as $key=>$value) {
             if (strlen($result)>1) {
                 $result .= '&';
             }
             $result .= urlencode($key) . '=' . urlencode($value);
         }
     } else {
         $result = '';
     }
     return $result;
 }


# returns link module cell for the release id
function releaseIdCell($relid, $exists) {
     $str = "<a href=$_SERVER[PHP_SELF]?selectType=existingReleases>$relid</a>";
     if ($exists=="TRUE") {
         return "<td bgcolor=yellow>$str</td>";
     } else {
         return "<td $str</td>";
     }
 }

# returns table cell for the release id
function releaseNumCell($relnum, $Nreleases) {
    $order = $Nreleases-$relnum+1;
    $str = "<a href=$_SERVER[PHP_SELF]?selectType=latestReleases title=\"Releases for the module. Click to show only latest module releases.\">$order/$Nreleases</a>";
    if ($order == 1) {
        # the latest release
        # need to return a link as well
        return "<td bgcolor=#BBAA00>$str</td>";
    } else {
        return "<td>$str</td>";
    }
 }

# returns table cell for the release id
function releaseLOCCell($filesChanged, $overallLOC, $addedLOC, $deletedLOC, $changedLOC) {
    if ($filesChanged !=0) {
        if ($overallLOC > 999) {
            $bgcolor = "#ec9571";
        } elseif ($overallLOC > 200) {
            $bgcolor = "#a3bb24";
        } elseif ($overallLOC > 30) {
            $bgcolor = "#ecd271";
        } else {
            $bgcolor = "#d9ecbf";
        }
        $str = "<font color=#550000><B>F</B>${filesChanged}</font>&nbsp;&nbsp;<font color=#0000FF><B>+</B>$addedLOC</font>&nbsp;&nbsp;<font color=#550000><B>-</B>$deletedLOC</font>&nbsp;&nbsp;<font color=#0000FF><B>!</B>$changedLOC</font>";
        return "<td bgcolor=$bgcolor>$str</td>";
    } else {
        return "<td>&nbsp</td>";
    }
}

# returns a color for row based on if it is a package, or module
# build/source release
function rowColor ($rowType) {
    switch ($rowType) {
    case "PACKAGE":
        $bgcolor = "#FFCCCC";
        #$bgcolor = "#00CCCC";
        break;
    case "SOURCE":
        $bgcolor = "#CCFFFF";
        break;
    case "BUILD":
        $bgcolor = "ivory";
        break;
    case "MAINTSOURCE":
        $bgcolor = "#CFCCFF";
        break;
    case "MAINTBUILD":
        $bgcolor = "#CCFFCC";
        break;
    default:
        #$bgcolor = "red";
        $bgcolor = "#FFCCCC";
    }
    return $bgcolor;
}

# returns the table cell for the release tag
function releaseTagCell($tag, $relid, $nrelatives, $type) {
    if ($nrelatives != 0) {
        $str = "$tag/$nrelatives";
        if ($type == "MODULE") {
            return "<td><a href=$_SERVER[PHP_SELF]?selectType=moduleReleasePackageReleases&selectTypeArgs=$relid title=\"Module release tag. Click to show package releases module '$tag' release belongs to.\">$str</a></td>";
        } else {
            return "<td><a href=$_SERVER[PHP_SELF]?selectType=packageReleaseModuleReleases&selectTypeArgs=$relid  title=\"Package release tag. Click to show module releases in the '$tag' package release\">$str</a></td>";
        }
    } else {
        return "<td bgcolor=#AAAAAA>$tag</td>";
    }
}

# returns the table cell for the build release number
function buildNumCell($build) {
    if ($build != "") {
        return "<td>$build</td>";
    } else {
        return "<td>&nbsp;</td>";
    }
}

# returns the table cell for the module/package name
function modpkgNameCell($name, $type) {
    if ($type == "MODULE") {
        return "<th><a href=$_SERVER[PHP_SELF]?selectType=specifiedModule&selectTypeArgs=" . urlencode($name) . "  title=\"Module name. Click to show only '$name' module releases.\">$name</a></th>";
    } else {
        return "<th><a href=$_SERVER[PHP_SELF]?selectType=specifiedPackage&selectTypeArgs=" . urlencode($name) . " title=\"Package name. Click to show only '$name' package releases.\">$name</a></th>";
    }
}

# returns the table cell for the user name
function userCell($user) {
    return "<td><a href=$_SERVER[PHP_SELF]?selectType=onlyUser&selectTypeArgs=$user title=\"User who made the release. Click to show only releases '$user'.\">$user</a></td>";
}

# returns the table cell for the release data
function dateCell($datetime) {
    #$dt = explode(" ", $datetime);
    $dt =  implode("--", explode(" ", $datetime));
    return "<td><a href=$_SERVER[PHP_SELF]?selectType=onlyDate&selectTypeArgs=$dt[0] title=\"Release date. Click to show only releases made on '$dt'.\">$dt</a></td>";
}

# returns the table cell for the release data
function branchesCell($branches) {
    $str = "";
    foreach (array_unique(explode(",",$branches)) as $i) {
        // with PHP 5.0, can pass a count argument to str_replace to
        // simplify the check for whether the substitution worked
        $br = str_replace("-DEAD", "", $i);
        if ($i != $br) {
            $clr = "red";
        } else {
            $clr = "green";
        }
        $str .=  "<font color=$clr>$br</font>";
    }
    return "<td>$str</td>";
}

# returns the table cell for the release data
function maintCell($maintBranch, $maintNum) {
    return "<td>${maintBranch}${maintNum}</td>";
}

# returns the table cell for the module/package id
function modpkgIdCell($modpkgId) {
    return "<td>${modpkgId}</td>";
}

# returns the table cell for the apiChanges data
function apiChangesCell($files, $relid, $obsrelsCount) {
    if ($files != "") {
        $str = str_replace(",", " ", $files);
        // echo "files=GGG$files GGG\n";
        return "<td bgcolor=#AAAA00><a href=$_SERVER[PHP_SELF]?selectType=obsoletedModuleReleases&selectTypeArgs=$relid title=\"Header changes in this release. Click to show module releases potentially incompatible with these changes.\">$str</a></td>";
    } else {
        return "<td>&nbsp;</td>";
    }
}

# returns the table cell for the bug Ids
function bugIdsCell($bugs, $bugsdata, $bugsdesc) {
    $bugsstr = "";
    #    $bugEntry_url = "http://dartslab.jpl.nasa.gov/internal/bugzilla/show_bug.cgi?id=";
    global $bugEntry_url;
    global $bugzillaPassword;
    ##$bugsstr="CCCC";
    foreach (explode(",",$bugs) as $i) {
        if ($i) {
            if ($bugzillaPassword) {
                if ($bugsdata[$i] == "NEW" || $bugsdata[$i] == "ASSIGNED" || $bugsdata[$i] == "REOPENED") {
                    $color = "#990000";
                } else {
                    $color = "#00CC00";
                }
                $bugsstr .= "<a href=$_SERVER[PHP_SELF]?selectType=bugid&selectTypeArgs=$i title=\"Click to show module releases related to the '$i' bug.\"><font color=#000055>*</font></a>";
                $bugsstr .= "<a href=${bugEntry_url}$i  title=\"$bugsdesc[$i]\"><font color=$color>$i</font></a> ";
            } else {
                $bugsstr = $i;
            }
        }
    }
    return "<td>${bugsstr}</td>";
}


# returns the table cell for the bug Ids
function bugIdsCellOBSOLETE($bugsres) {
    $bugsstr = "";
#    $bugEntry_url = "http://dartslab.jpl.nasa.gov/internal/bugzilla/show_bug.cgi?id=";
    global $bugEntry_url;
    while ($id = mysqli_fetch_row($bugsres)) {
        $bugsstr .= "<a href=${bugEntry_url}$id[0]>$id[0]</a> ";
    }
    ##$bugsstr="CCCC";
    return "<td>${bugsstr}</td>";
}


# returns the table cell for the apiChanges data
function obsoleteReleasesCell($napis, $relid) {
    if ($napis != 0) {
        return "<td bgcolor=#FF6600><a href=$_SERVER[PHP_SELF]?selectType=apiChangeModuleReleases&selectTypeArgs=$relid title=\"Number of releases obsolescing this release. Click to show these module releases.\">$napis</a></td>";
    } else {
        return "<td>&nbsp;</td>";
    }
}


# returns the table cell for the release data
function readmesCell($readmes, $type, $reltag, $build) {
    global $changelogDir_url;
    global $changelogs_path;
    $str = "";
    if ($type == 'PACKAGE') {
      $prefix = "package-$reltag";
      $readmes = "ReleaseNotes";
    } else {
        $prefix = "module-$reltag";
        if ($build != "") {
            $prefix .= "-Build$build";
        }
    }
    foreach (explode(", ",  $readmes) as $file) {
        switch ($file) {
        case "ChangeLog":
            $abbrev = "CL";
            break;
        case "ReleaseNotes":
            $abbrev = "RN";
            break;
        case "Readme":
            $abbrev = "RM";
            break;
        default:
            $abbrev = $file;
        }
        # $fpath = "$changelogs_path/$prefix-$file";
        if (readlink($fpath))
           {
              $str .= "<a href=$changelogDir_url/$prefix-$file title=\"Link to the '$file' file\">$abbrev</a> ";
           }
        else
           {
              $str .= " $abbrev " ;
           }
    }
    return "<td>$str</td>";
}


# dumps an array
function dumpArray ($title, $a) {
    echo "Array $title:<br>";
    foreach ($a as $postname=>$postvalue) {
        echo("name=" . $postname . " val=" . $postvalue . "<br>");
    }
}


# returns an array with extensions to the 'ORDER'
# query string
function sortSQL ($type) {

    switch ($type) {
    case "Name":
        $str = "modulePackages.name ";
        break;
    case "User":
        $str = "modpkgReleases.user ";
        break;
    case "Date":
        $str = "modpkgReleases.datetime ";
        break;
    case "":
        $str = "modpkgReleases.datetime ";
        break;
    default:
        echo "Unknown sort type: $type\n";
    }
    return $str;
}


# returns an array with extensions to the 'FROM' and 'WHERE' SQL
# query string for the specific query type
function selectSQL ($type, $param="") {

    $selectSQL["WHERE"] = "";
    $selectSQL["FROM"] = "";
    $selectSQL["desc"] = "";

    switch ($type) {
    case "latestReleases":
        # no additional inputs
        #$selectSQL["WHERE"] = "and Nreleases=relnum";
        $selectSQL["WHERE"] = "and modulePackages.latestRelid=modpkgReleases.relid";
        $selectSQL["desc"] = "Latest module/package releases only." ;
        break;
    case "moduleReleasePackageReleases":
        # needs a module name, release tag and build
        $rel = splitReleaseName($param);
        $selectSQL["FROM"] = ", packageModuleReleases";
        $selectSQL["WHERE"] = "and packageModuleReleases.modrelid=\"$param\" and modpkgReleases.relid=packageModuleReleases.pkgrelid";
        $selectSQL["desc"] = "Only package releases containing $param module release." ;
        break;
    case "packageReleaseModuleReleases":
        # needs a package name, release tag
        $rel = splitReleaseName($param);
        $selectSQL["FROM"] = ", packageModuleReleases";
        $selectSQL["WHERE"] = "and packageModuleReleases.pkgrelid=\"$param\" and modpkgReleases.relid=packageModuleReleases.modrelid";
        $selectSQL["desc"] = "Only module releases contained in $param package release." ;
        break;
    case "bugid":
        # needs a package name, release tag
        $rel = splitReleaseName($param);
        # $selectSQL["FROM"] = ", packageModuleReleases, releaseBugIds as rBugIds";
        # $selectSQL["WHERE"] = "and rBugIds.bugid=\"$param\" and modpkgReleases.relid=rBugIds.relid";
        $selectSQL["FROM"] = "";
        $selectSQL["WHERE"] = "and bugid=\"$param\" ";
        $selectSQL["desc"] = "Only module releases effecting the $param bug id." ;
        break;
    case "existingReleases":
        # no additional inputs
        $selectSQL["WHERE"] = "and existing=1";
        $selectSQL["desc"] = "Only link module releases that are still in the release area.";
        break;
    case "specifiedModule":
        # module name
        $selectSQL["FROM"] = ", modulePackages as module";
        $selectSQL["WHERE"] = "and module.name=\"$param\" and module.id=modpkgReleases.modpkgId";
        $selectSQL["desc"] = "Only releases for the $param module." ;
        break;
    case "specifiedPackage":
        # package name
        $selectSQL["FROM"] = ", modulePackages as package";
        $selectSQL["WHERE"] = "and package.name=\"$param\" and package.id=modpkgReleases.modpkgId";
        $selectSQL["desc"] = "Only releases for the $param package." ;
        break;
    case "onlyUser":
        # user name
        $selectSQL["WHERE"] = "and user=\"$param\"";
        $selectSQL["desc"] = "Only releases by the $param user." ;
        break;
    case "onlyDate":
        # the date
        $selectSQL["WHERE"] = "and DATE_FORMAT(datetime, '%Y-%m-%d')=\"$param\"";
        $selectSQL["desc"] = "Only releases made on the $param date." ;
        break;
    case "betweenDates":
        # view entries between two dates
        list($startDate, $endDate) = explode(",", $param);
        $selectSQL["WHERE"] = "and DATE_FORMAT(datetime, '%Y-%m-%d') <= \"$startDate\"";
        $selectSQL["desc"] = "Only releases made starting from $startDate.";
        break;
    // case "skipBuilds":
    //     $selectSQL["WHERE"] = " and build IS NULL";
    //     $selectSQL["desc"] = "Only non-build releases";
    //     break;
    case "obsoletedModuleReleases":
        # the module name, tag and build with API changes
        $selectSQL["FROM"] = ", obsoleteRels";
        $selectSQL["WHERE"] = "and obsoleteRels.apirelid=\"$param\" and modpkgReleases.relid=obsoleteRels.obsrelid";
        $selectSQL["desc"] = "Only module releases made obsolete by the $param module release.";
        break;
    case "apiChangeModuleReleases":
        # the module name, tag and build effected by API changes
        $selectSQL["FROM"] = ", obsoleteRels";
        $selectSQL["WHERE"] = "and obsoleteRels.obsrelid=\"$param\" and modpkgReleases.relid=obsoleteRels.apirelid";
        $selectSQL["desc"] = "Only module releases containing API changes that have made the $param module release obsolete." ;
        break;
    case "":
        # nothing to do
        $selectSQL[] = "";
        $selectSQL["desc"] = "";
        break;
    default:
        echo "Unknown selection type: $type\n";
    }

    return $selectSQL;
}

function buildSQL ($type, $param="") {
    switch ($type) {
        case "skipBuilds":
            $buildSQL["WHERE"] = " and build IS NULL";
            $buildSQL["desc"] = "Only non-build releases";
            break;
        case "keepBuilds":
            $buildSQL["WHERE"] = "";
            break;
        default:
            echo "Unknown buildSQL type: $type\n";
        }
        return $buildSQL;
}

# takes a full release tag, eg. Darts-R3-22alpha or Darts-R3-22alphs-Build05
# and returns an array with 6 elements - 0 -> original tag, 1 -> Darts,
# 2 -> '3', 3 -> '22', 4 -> 'alpha', 5 -> '05'. Note that the last element
# is not set if the specified string was not a build release tag
function splitReleaseName ($release) {
    # try a build release pattern, followed by a regular release pattern
    if (!preg_match("/(.+?)\-R(\\d)\-(\\d*)([^\-\s]*)\-Build(\\d*)/", $release, $matches)) {
        preg_match("/(.+?)\-R(\\d)\-(\\d*)([^\-\s]*)/", $release, $matches);
    }
    #echo "ddd $matches[0], $matches[1], $matches[2], $matches[3], $matches[4], $matches[5]\n";
    $x['name'] = $matches[1];
    $x['tag'] = "R$matches[2]-$matches[3]$matches[4]";
    $x['build'] = $matches[5];
    return $x;
}

// `DEFAULTS if nothing is set yet
if (!isset($_GET["selectType"])) {
    $_GET["selectType"] = "";
}

if (!isset($_GET["buildType"])) {
    $_GET["buildType"] = "keepBuilds";
}

if (!isset($_GET["selectTypeArgs"])) {
    $_GET["selectTypeArgs"] = "";
}

if (!isset($_GET["prevSortType"]) || $_GET["prevSortType"] == "") {
    $_GET["prevSortType"] = "Date";
}
// if (!isset($_GET["prevBuildType"]) || $_GET["prevBuildType"] == "") {
//     $_GET["prevSortType"] = "keepBuilds";
// }
if (!isset($_GET["buildType"]) || $_GET["buildType"] == "") {
    $_GET["prevSortType"] = "keepBuilds";
}
if (!isset($_GET["sortType"])) {
    $_GET["sortType"] = "Date";
}

if (!isset($_GET["prevSortDir"])) {
    $_GET["prevSortDir"] = "DESC";
}

if (!isset($_GET["page"])) {
    $page = 1;
} else {
    $page = $_GET["page"];
}

if (!isset($_GET["prevPage"])) {
    $_GET["prevPage"] = "";
}
$sortDir = $_GET["prevSortDir"];
$buildType = $_GET["buildType"];
// $buildType = $_GET["prevBuildType"];


# -- keep previous sort direction and type if merely selecting a new page in the search
# -- don't care about sort direction if using a new sort type
# -- toggle sort direction if the sort type is the same, and the page is
#    the same

# toggle the sort direction if the same sort type is requested, and we are
# staying on the same page
// if (($page == $_GET["prevPage"]) &&
//     ($_GET["sortType"] == $_GET["prevSortType"])) {
//     if ($_GET["prevSortDir"] == "ASC") {
//         $sortDir = "DESC";
//     } else {
//         $sortDir = "ASC";
//     }
// }

$str = $title;
$str .= "<b style=\"padding:12px\"> YaM Project: <font color=black> $project</font></b>";
// Commentiong out line below as it was deemed as high risk. Uncomment at your own risk.
//$str .= "&nbsp;&nbsp;<input type=\"submit\" name=\"ClearSelection\" value=\"Clear selection\">&nbsp;&nbsp;";

// $str .= "&nbsp;&nbsp;Skip Build Releases";
// $str .= "<label class=\"switch\">  <input type=\"checkbox\" name=\"skipbuildrels\" value=\"Yes\" >    <span class=\"slider round\"></span></label>";

#===========================================
# YaM queries
$db = mysqli_connect($mysqlPort, $mysqlUser, $mysqlPassword);

$db->select_db("YaM$project");

$selectStr = selectSQL($_GET["selectType"],$_GET["selectTypeArgs"]);
$sortStr = sortSQL($_GET["sortType"]);
$buildStr = buildSQL($_GET["buildType"]);

$fieldsstr =     "modulePackages.name, " .
    "modpkgReleases.modpkgId, " .
    "modpkgReleases.relid, " .
    "modpkgReleases.datetime, " .
    "modpkgReleases.relnum, " .
    "modulePackages.Nreleases, " .
    "modpkgReleases.type as releaseType, " .
    "modulePackages.type as modpkgType, " .
    "modpkgReleases.tag, " .
    "modpkgReleases.build, " .
    "modpkgReleases.maintBranch, " .
    "modpkgReleases.maintNum, " .
    "modpkgReleases.user, " .
    "modpkgReleases.branches, " .
    "modpkgReleases.filesChanged, " .
    "modpkgReleases.overallLOC, " .
    "modpkgReleases.addedLOC, " .
    "modpkgReleases.removedLOC, " .
    "modpkgReleases.changedLOC, " .
    "modpkgReleases.readmes, " .
    "modpkgReleases.existing, " .
    "modpkgReleases.nrelatives, " .
    "modpkgReleases.obsoletionCount, " .
    "modpkgReleases.apiChangedFiles, " .
    "GROUP_CONCAT(releaseBugIds.bugid SEPARATOR ',') as bugs";

# use left join so we pick up relids that do not have entries in the
# releaseBugIds table (see http://www.wellho.net/mouth/158_MySQL-LEFT-JOIN-and-RIGHT-JOIN-INNER-JOIN-and-OUTER-JOIN.html)
$fromstr = "FROM modulePackages, modpkgReleases LEFT JOIN releaseBugIds ON (modpkgReleases.relid=releaseBugIds.relid) " . $selectStr["FROM"];
$where = "WHERE modulePackages.id=modpkgReleases.modpkgId " . $selectStr["WHERE"] . $buildStr["WHERE"];

if ($_GET['skipbuildrels'] == "Yes") {
     $where .= " and build IS NULL";
}

$orderstr = "ORDER BY $sortStr $sortDir";
if ($_GET["sortType"] != "Date") {
    $orderstr .= ", modpkgReleases.datetime DESC";
}

$limit = 50;
$limitvalue = $page * $limit - ($limit);
$limstr = "LIMIT $limitvalue, $limit";

$groupstr = "GROUP BY modpkgReleases.relid";

#============================
# get the number of rows
# $lenstr = "SELECT COUNT(modpkgReleases.relid) as total $fromstr $where";
$result = $db->query($lenstr);
if (!$result) {
    echo("error" . "<br>\n");
}
$myrow = mysqli_fetch_array($result);
$totalrows = $myrow["total"];

#============================
# get the actual data
# Commenting line below as it was deemded as high risk. Uncomment at your own discretion.
# $qry = "SELECT $fieldsstr $fromstr $where $groupstr $orderstr $limstr";
// echo($qry);
// echo("\n____________________________\n");
$result = $db->query($qry);

if (!$result) {
    echo "error" . "<br>\n";
}

# get the value of the opposite sort direction to the current one
$newSortDir = flipSortDir($sortDir);

if ($myrow = mysqli_fetch_array($result)) {
    $sortcolor = "LightCoral";
    $namecolor = "";
    $usercolor = "";
    $datecolor = "";
    switch ($_GET["sortType"]) {
    case "Name":
        $namecolor = "bgcolor=$sortcolor";
        break;
    case "User":
        $usercolor = "bgcolor=$sortcolor";
        break;
    case "Date":
        $datecolor = "bgcolor=$sortcolor";
        break;
    default:
    }

    # save variables that we need to pass to the pagination index for use
    # in creating the index
    // $save["prevBuildType"] = $_GET["buildType"];
    $save["buildType"] = $_GET["buildType"];
    $save["prevSortType"] = $_GET["sortType"];
    $save["prevSortDir"] = $sortDir;
    $save["prevPage"] = $page;
    if ($_GET["selectType"]) {
        $save["selectType"] = $_GET["selectType"];
        $save["selectTypeArgs"] = $_GET["selectTypeArgs"];
    }
    if ($_GET['skipbuildrels'] == "Yes") {
        $save["skipbuildrels"] = "Yes";
    }

    $url = $_SERVER["PHP_SELF"] .  httpimplode($save, $quma = true);

    # create the pagination index
    $str .=  "<br>";
    $maxlimit = $limitvalue+$limit;
    if ($maxlimit > $totalrows) {
        $maxlimit = $totalrows;
    }

    //`STUFF ABOVE TABLE
    $str .= "<div class=col-md-1 style=\"float:left;\">";
    # Commenting out this line as it yeilds a high risk error in code checks. Uncomment at your own risk:
    # $str .= "<input type=text name=from_date id=from_date class=form-control placeholder=\"Start Date\" />";
    $str .= "</div>";

    // $str .= "<div class=col-md-1 style=float:left>";
    // $str .= "<input type=text name=to_date id=to_date class=form-control placeholder=\"End Date\" />";
    // $str .= "</div>";

    $str .= "<div class=col-md-5 style=float:left>";
    $str .= "<input type=button name=filter1 id=filterTEST1 value=\"Filter by Date\" class=\"btn btn-info\"/>";
    $str .= "</div>";

    $str .= "<div name=builddiv id=builddiv class=col-md-5 style=float:left>";
    // $str .= "<input type=button name=buildfilter id=buildfilter value=\"Skip Builds\" class=\"btn btn-info\"/>";
    // $str .= "<input type=button name=buildfilter2 id=buildfilter2 value=\"Show Builds\" class=\"btn btn-info\"/>";
    $str .= "<input type=button value=\"Skip Builds\" id=myButton1></input>";
    // $str .= "<p id=myText1>Showing Builds</p>";
    // $str .= "<button onClick=\"changeItemStatus('{!\$Component.bVAL}', '{!item.Id}'); return false;\" >{!IF(orders[item.Id] > 0, 'Hello', 'Goodbye')}</button>";
    // <button onClick="changeItemStatus('{!$Component.bVAL}', '{!item.Id}'); return false;" >{!IF(orders[item.Id] > 0, 'Hello', 'Goodbye')}</button>
    $str .= "</div>";

//#---------------------------------------------------

//<!-- #--------------------------------------------------- -->
//<!-- `TOP PAGINATION HERE -->

$page_no=$_GET["page"];
if (empty($page_no)) {
    $previous_page = 0;
    $next_page = 2;
    $page_no = 1;
} else {
    $previous_page = $page_no - 1;
    $next_page = $page_no + 1;
}


$total_no_of_pages=ceil($totalrows / $limit);


$str .= '<div style="margin:auto; width:25%;">';
$str .= '<ul class="pagination">';

if  ($page_no > 1)  {
         $str .=  "<li><a href=\"$url&page=1\">First Page</a></li>";
}


# add Previous button if not on the first page
$str .= "\n<li ";
if($page_no <= 1) {
            $str .= " class='disabled'";
}
$str .= ">\n <a";

if($page_no > 1) {
  $str .=    " href=\"$url&page=$previous_page\"";
}
$str .=    "> Previous </a>\n </li>\n";




# add Next button if not on the last page
$str .= "<li  ";
if($page_no >= $total_no_of_pages) {
            $str .= " class='disabled'";
}
$str .= ">\n<a";

if($page_no < $total_no_of_pages) {
  $str .=    " href=\"$url&page=$next_page\"";
}
$str .=    "> Next </a>\n </li>\n";

# add last page button if the number of pages is < 100
if  ($page_no < $total_no_of_pages && $total_no_of_pages < 100)  {
       $str .= "<li>\n<a href=\"$url&page=$total_no_of_pages\"> Last &rsaquo;&rsaquo;</a>\n</li>\n";
}

$str .= "&nbsp&nbsp<li>\n Page $page_no";
$str .=  "/";
$str .=  "$total_no_of_pages\n</li>&nbsp&nbsp\n";



$str .= '</ul>';
$str .= '</div>';

//#--------------------------------------------------------------


    $str .= "<b><font color=red style=\"float:left\"> $selectStr[desc] Displaying <font color=blue>" . ($limitvalue+1) . "-$maxlimit</font> out of <font color=blue>$totalrows</font> available release entries.</font></b><br>";
    $str .= "<table id=order_table class=table border=1>\n";
    $str .= "<thead>";
    $str .= "<tr bgcolor=lightgreen>";

    // `TABLE FIELDS
    $str .=  "<th title='The unique release id for this release' >RelId</th> ";
    $str .=  "<th title='The order/total number of releases for this module/package. The latest relase has order=1. Clicking on any of these entries will narrow down the listing to only latest releases.'>Seq</th> ";
    $str .=  "<th title='The unique id for this module/package'>Id</th>";
    $str .=  "<th $namecolor title='Module/package for this release. CLicking on an entry will narrow down the listing to the releases for just this module/package'><a href=$url&sortType=Name&selectType=$_GET[selectType]&selectTypeArgs=$_GET[selectTypeArgs]&prevSortDir=$newSortDir title=\"Click to sort by module/package name\">Name</a></th> ";
    $str .=  "<th title='The release tag for this release. More a module release, clicking on such an entry will switch to a page containing the list of package releases that use this module release. For a package release, clicking on such an entry will switch to a page containing the list of module release belonging to this package release.'>Tag</th> ";
    $str .=  "<th title='Build release number if this were a module build release'>Build</th>";
    $str .=  "<th $usercolor title='User who made this release. Clicking on one of these links will narraw the page to just the releases made by this user.'><a href=$url&sortType=User&selectType=$_GET[selectType]&selectTypeArgs=$_GET[selectTypeArgs] title=\"Click to sort by user name\">User</a></th> ";
    $str .=  "<th $datecolor title='Date & time of this release'><a href=$url&sortType=Date&selectType=$_GET[selectType]&selectTypeArgs=$_GET[selectTypeArgs] title=\"Click to sort by date\"> Date & time </a></th> ";
    $str .=  "<th title='Branches that have been created from this release'>Branches</th>";
    $str .=  "<th title='Maintenance release tag if this this is a maintenance release' >MaintRel</th>";
    $str .=  "<th title='Bug ids fixed in this release'>Bugs</th>";
    $str .=  "<th title='Lines of code change summary'>SLOC</th>";
    $str .=  "<th title='Links to ChangeLog, ReleaseNotes etc files for this release.'>&nbsp&nbsp Readmes&nbsp&nbsp</th>";
    $str .=  "<th title='Header files that have changed in this release and potentially indicating C++ level API changes. Clicking on any file link will create a page with user module releases that may have been obsoleted by this header file change.'>API changes</th>";
    $str .=  "<th title='Number of subsequent module releases that have made this release obsolete. Clicking on any such link will create a page with module releases that have made this release obsolete.'>Obsolete</th> </tr>\n";
    $str .= "</thead>";
    do {
        $str .= "<tbody>";
        $rowColor = rowColor($myrow["releaseType"]);
        $str .= ("<tr bgcolor=$rowColor>");
        $str .=  releaseIdCell($myrow["relid"], $myrow["existing"]);
        $str .=  releaseNumCell($myrow["relnum"], $myrow["Nreleases"]);
        $str .=  modpkgIdCell( $myrow["modpkgId"] );
        $str .=  modpkgNameCell($myrow["name"], $myrow["modpkgType"]);
        $str .=  releaseTagCell($myrow["tag"], $myrow["relid"],
                                $myrow["nrelatives"],
                                $myrow["modpkgType"]);
        $str .=  buildNumCell($myrow["build"]);
        $str .=  userCell($myrow["user"]);
        $str .=  dateCell($myrow["datetime"]);
        $str .=  branchesCell($myrow["branches"]);
        $str .=  maintCell($myrow["maintBranch"], $myrow["maintNum"]);
        $str .=  bugIdsCell( $myrow["bugs"], $bugsdata, $bugsdesc );
        $str .=  releaseLOCCell($myrow["filesChanged"], $myrow["overallLOC"],
                                $myrow["addedLOC"], $myrow["removedLOC"],
                                $myrow["changedLOC"]);
        $str .=  readmesCell($myrow["readmes"], $myrow["modpkgType"],
                             "$myrow[name]-$myrow[tag]", $myrow["build"]
                             );
        $str .=  apiChangesCell($myrow["apiChangedFiles"], $myrow["relid"], $myrow["obsrelsCount"]);
        $str .=  obsoleteReleasesCell($myrow["obsoletionCount"], $myrow["relid"]);
        $str .= ("</tr>\n");
        $str .= "</tbody>";

    } while ($myrow = mysqli_fetch_array($result));
    $str .=  "</table>\n";
} else {
    $str .- "<br/>";
    $str .=  "Sorry, no records were found!";
}
// OLD PAGINATION
// $str .= pagination ($page, $limit, $totalrows, $url);

echo $str;
?>

<!-- #--------------------------------------------------- -->
<!-- `NEW PAGINATION HERE -->

<div style="margin:auto; width:25%;">
<ul class="pagination">
<?php
$page_no=$_GET["page"];
if (empty($page_no)) {
    $previous_page = 0;
    $next_page = 2;
    $page_no = 1;
} else {
    $previous_page = $page_no - 1;
    $next_page = $page_no + 1;
}


$total_no_of_pages=ceil($totalrows / $limit);

if($page_no > 1){
echo "<li><a href=\"$url&page=1\">First Page</a></li>";
} ?>


<li <?php if($page_no <= 1){ echo "class='disabled'"; } ?>>
<a <?php if($page_no > 1){

echo "href=\"$url&page=$previous_page\"";
} ?>>Previous</a>
</li>




<li <?php if($page_no >= $total_no_of_pages){
echo "class='disabled'";
} ?>>
<a <?php
if($page_no < $total_no_of_pages) {
echo "href=\"$url&page=$next_page\"";
} ?>>Next</a>
</li>




<?php if($page_no < $total_no_of_pages && $total_no_of_pages < 100){
echo "<li><a href=\"$url&page=$total_no_of_pages\">Last &rsaquo;&rsaquo;</a></li>";
} ?>

&nbsp&nbsp<li> <?php echo "\nPage $page_no/$total_no_of_pages\n" ?></li>&nbsp&nbsp

</ul>
</div>

<!-- #--------------------------------------------------- -->

<?php
mysqli_free_result($result);
?>
</form>
</body>
</html>

<script type="module">
    // import React from 'react';

    $(document).ready(function(){
        // var elem = document.getElementById("myText1");
        // if(location.href.includes("buildType=skipBuilds")){
        //     elem.innerHTML = "Skipping Builds";
        // } else {
        //     elem.innerHTML = "Showing Builds";
        // }


        // if (location.href.includes("prevBuildType=skipBuilds")) {
        //     location.assign(location.href + "&buildType=skipBuilds");
        // }
        var elem = document.getElementById("myButton1");
        if(location.href.includes("buildType=skipBuilds") || location.href.includes("prevBuildType=skipBuilds")){
            elem.value = "Show Builds";
        } else {
            elem.value = "Skip Builds";
        }
        $.datepicker.setDefaults({
            dateFormat: 'yy-mm-dd'
        });
        $(function(){
            $("#from_date").datepicker();
            $("#to_date").datepicker();
        });
        console.log(location.href);
        // $('#buildfilter').click(function(){
        //     document.form.buildfilter.value = "Include Builds";
        //     // $("#buildfilter").html("Button New Text");
        //     if(location.href.includes(".php?")) {
        //         location.assign(location.href + "&buildType=skipBuilds");
        //     }
        //     else {
        //         location.assign(location.href + "?buildType=skipBuilds");
        //     }
        // })
        $('#filterTEST1').click(function(){
            var from_date = $('#from_date').val();
            var to_date = $('#to_date').val();
            console.log(from_date);
            console.log(to_date);
            console.log(to_date<from_date);
            console.log(from_date<to_date);
            if(from_date != '')
            {
                if(location.href.includes(".php?")) {
                    location.assign(location.href + "&selectType=betweenDates&selectTypeArgs=" + from_date);
                }
                else {
                    location.assign(location.href + "?selectType=betweenDates&selectTypeArgs=" + from_date);
                }
            }
            else
            {
                alert("Please Select Date.");
            }
        })
        $('#myButton1').click(function(){
            console.log("toggle clicked");
            var elem = document.getElementById("myButton1");
            // TO SHOW BUILDS
            if (elem.value=="Show Builds") {
                if(location.href.includes("&buildType=skipBuilds")) {
                    location.assign(location.href.replace("&buildType=skipBuilds", ''))
                } else if(location.href.includes("?buildType=skipBuilds")) {
                    location.assign(location.href.replace("buildType=skipBuilds", ''))
                }
            }
            // TO SKIP BUILDS
            else {
                if(!location.href.includes("buildType=skipBuilds")){
                    if(location.href.includes(".php?")) {
                    location.assign(location.href + "&buildType=skipBuilds");
                    }
                    else {
                        location.assign(location.href + "?buildType=skipBuilds");
                    }
                }
            }
        })
    })


</script>