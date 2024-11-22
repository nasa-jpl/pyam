//basic Node API for accessing the SQL server. 
//Currently, the only db query that this can make is the query that is made through the php code in the index.php file.
//to run, first run "npm i" to install dependencies.
//Then run "node app.js" to start the server 
//(or you can use nodemon for easier development)
const express = require("express");
const db = require("./db");
const cors = require("cors");

const app = express();

const PORT = 3002;
app.use(cors());
app.use(express.json());

db.connect();

// $qry = "SELECT $fieldsstr $fromstr $where $groupstr $orderstr $limstr";

app.get("/", (req, res) => {
  res.send("Successful response.");
});

//SELECT COUNT(modpkgReleases.relid) as total FROM modulePackages, modpkgReleases LEFT JOIN releaseBugIds ON (modpkgReleases.relid=releaseBugIds.relid) WHERE modulePackages.id=modpkgReleases.modpkgId

let splitReleaseName = (release) => {
  // try a build release pattern, followed by a regular release pattern
  let buildPattern = /(.+?)-R(\d)-(\d*)([^\-\s]*)-Build(\d*)/;
  let woBuildPattern = /(.+?)-R(\d)-(\d*)([^\-\s]*)/;
  let matches = buildPattern.test(release)
    ? buildPattern.exec(release)
    : woBuildPattern.exec(release);
  split = {};
  split["name"] = matches[1];
  split["tag"] = matches[2] + "-" + matches[3] + matches[4]; // "R$matches[2]-$matches[3]$matches[4]";
  split["build"] = matches.length == 6 ? matches[5] : "";
  return split;
};

let selectSQL = (type="", param="") => {
  var selection = {};

  switch (type) {
    case "latestReleases":
      // no additional inputs
      //#selection["WHERE"] = "and Nreleases=relnum";
      selection["WHERE"] =
        "and modulePackages.latestRelid=modpkgReleases.relid";
      selection["desc"] = "Latest module/package releases only.";
      break;
    case "moduleReleasePackageReleases":
      // needs a module name, release tag and build
      rel = splitReleaseName(param);
      selection["FROM"] = ", packageModuleReleases";
      selection["WHERE"] =
        `and packageModuleReleases.modrelid="${param}" and modpkgReleases.relid=packageModuleReleases.pkgrelid`;
      selection["desc"] =
        `Only package releases containing ${param} module release.`;
      break;
    case "packageReleaseModuleReleases":
      // needs a package name, release tag
      rel = splitReleaseName(param);
      selection["FROM"] = ", packageModuleReleases";
      selection["WHERE"] =
        `and packageModuleReleases.pkgrelid="${param}" and modpkgReleases.relid=packageModuleReleases.modrelid`;
      selection["desc"] =
        `Only module releases contained in ${param} package release.`;
      break;
    case "bugid":
      // needs a package name, release tag
      rel = splitReleaseName($param);
      // selection["FROM"] = ", packageModuleReleases, releaseBugIds as rBugIds";
      // selection["WHERE"] = "and rBugIds.bugid=\"$param\" and modpkgReleases.relid=rBugIds.relid";

      selection["FROM"] = "";
      selection["WHERE"] = `and bugid="${param}" `;
      selection["desc"] = `Only module releases effecting the ${param} bug id.`;
      break;
    case "existingReleases":
      // no additional inputs
      selection["WHERE"] = "and existing=1";
      selection["desc"] =
        "Only link module releases that are still in the release area.";
      break;
    case "specifiedModule":
      // module name
      selection["FROM"] = ", modulePackages as module";
      selection["WHERE"] =
        `and module.name="${param}" and module.id=modpkgReleases.modpkgId`;

      selection["desc"] = `Only releases for the ${param} module.`;
      break;
    case "specifiedPackage":
      // package name
      selection["FROM"] = ", modulePackages as package";
      selection["WHERE"] =
        `and package.name="${param}" and package.id=modpkgReleases.modpkgId`;
      selection["desc"] = `Only releases for the ${param} package.`;
      break;
    case "onlyUser":
      // user name
      selection["WHERE"] = `and user="${param}"`;

      selection["desc"] = `Only releases by the ${param} user.`;
      break;
    case "onlyDate":
      // the date
      selection["WHERE"] = `and DATE_FORMAT(datetime, '%Y-%m-%d')=\"${param}\"`;
      selection["desc"] = `Only releases made on the ${param} date.`;
      break;
    case "obsoletedModuleReleases":
      // the module name, tag and build with API changes
      selection["FROM"] = ", obsoleteRels";
      selection["WHERE"] =
        `and obsoleteRels.apirelid="${param}" and modpkgReleases.relid=obsoleteRels.obsrelid`;
      selection["desc"] =
        `Only module releases made obsolete by the ${param} module release.`;
      break;
    case "apiChangeModuleReleases":
      // the module name, tag and build effected by API changes
      selection["FROM"] = ", obsoleteRels";
      selection["WHERE"] =
        `and obsoleteRels.obsrelid="${param}" and modpkgReleases.relid=obsoleteRels.apirelid`;
      selection["desc"] =
        `Only module releases containing API changes that have made the ${param} module release obsolete.`;
      break;
    case "":
      // nothing to do
      selection["FROM"] = "";
      selection["WHERE"] = "";
      selection["desc"] = "";
      break;
    default:
      console.log("Unknown selection type: $type\n");
  }

  return selection;
};

// Route for counting rows
app.get("/count", (req, res) => {
  //console.log("HEY THERE");
  const fromstr = req.body.fromstr;
  const where = req.body.where;

  // selectq = "SELECT COUNT(modpkgReleases.relid) as total ";
  fromq =
    "FROM modulePackages, modpkgReleases LEFT JOIN releaseBugIds ON (modpkgReleases.relid=releaseBugIds.relid) ";
  whereq = "WHERE modulePackages.id=modpkgReleases.modpkgId";
  qry = selectq + fromq + whereq;

  db.query(qry, (err, result) => {
    if (err) {
      console.log(err);
    }
    ans = JSON.stringify(result);
    json = JSON.parse(ans);

    console.log("Count: ", json[0].total);

    res.json(json[0].total);
  });
  //db.end();
});

app.get("/selectsql", (req, res) => {
  const type = req.query.selectType;
  const param = req.query.selectTypeArgs;
  console.log(type)
  console.log(param)
  let selection = selectSQL(type, param);
  let fromstr =
    "FROM modulePackages, modpkgReleases LEFT JOIN releaseBugIds ON (modpkgReleases.relid=releaseBugIds.relid) " +
    selection["FROM"];
  let where =
    "WHERE modulePackages.id=modpkgReleases.modpkgId " + selection["WHERE"];
  let qry = `SELECT COUNT(modpkgReleases.relid) as total ${fromstr} ${where}`;
  console.log(qry);
  db.query(qry, (err, result) => {
    if (err) {
      console.log(err);
    }
    ans = JSON.stringify(result);
    json = JSON.parse(ans);

    console.log("Count: ", json[0].total);

    res.json(json[0].total);
  });
});

app.listen(PORT, () => {
  console.log(`Server is running on ${PORT}`);
});
