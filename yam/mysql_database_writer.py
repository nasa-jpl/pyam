"""Contains SQL implementation of DatabaseWriter class."""

from __future__ import absolute_import

import contextlib
import re

from mysql import connector

from . import mysql_database_reader

from . import database
from . import database_writer
from . import mysql_database_utils
from . import name_utils
from . import yam_exception
from . import yam_log


class MySQLDatabaseWriter(database_writer.DatabaseWriter):
    """SQL implementation of database_writer.

    The implementation assumes the tables are stored using the MyISAM storage
    engine, which is non-transactional. Thus there are no commit or rollback
    calls.

    """

    def __init__(self, hostname, port, username, password, database_name):
        """Initialization."""
        database_writer.DatabaseWriter.__init__(self)
        self.__hostname = hostname
        self.__port = port
        self.__username = username
        self.__password = password
        self.__database_name = database_name

        self.__deferred_connection = None

    def __enter__(self):
        """Return instance on entering context."""
        return self

    def __exit__(self, _, __, ___):
        """Close on exiting context."""
        self.close()

    def close(self):
        """Close any open connections."""
        if self.__deferred_connection:
            self.__deferred_connection.close()
            self.__deferred_connection = None

    def append_branch(self, module_name, revision_tag, branch_id):
        """SQL implementation of database_writer.append_branch()."""
        module_name = name_utils.filter_module_name(module_name)

        # Get release ID from database.
        result = self.__fetch_one(
            """
SELECT modpkgReleases.relid
FROM modpkgReleases,
     modulePackages
WHERE modpkgReleases.modpkgId=modulePackages.id
    and modulePackages.type='MODULE'
    and modpkgReleases.build IS NULL
    and name=%s
    and tag=%s LIMIT 1""",
            module_name,
            revision_tag,
        )

        if not result:
            raise yam_exception.YamException(
                "Could not find module '{name}' with revision tag {tag} in "
                "database".format(name=module_name, tag=revision_tag)
            )

        assert "relid" in result
        release_id = result["relid"]

        # Use the release ID to update the branch list in the 'modulePackages'
        # table.
        self.__execute(
            """
UPDATE modpkgReleases
SET branches=CONCAT_WS(", ", branches, %s)
WHERE relid=%s""",
            branch_id,
            release_id,
        )

    def rename_branch(self, module_name, revision_tag, branch_id, new_branch_id):
        """SQL implementation of database_writer.rename_branch()."""
        module_name = name_utils.filter_module_name(module_name)

        # Branch names are already checked at a higher level. But assert to be
        # sure. Commas in branch names would be extremely bad given the way the
        # database tables are set up.
        assert "," not in branch_id
        assert "," not in new_branch_id

        # Get release ID from database.
        yam_log.say("Getting release ID for the {} module from the database".format(module_name))
        result = self.__fetch_one(
            """
SELECT modpkgReleases.relid
FROM modpkgReleases,
     modulePackages
WHERE modpkgReleases.modpkgId=modulePackages.id
    and modulePackages.type='MODULE'
    and modpkgReleases.build IS NULL
    and name=%s
    and tag=%s LIMIT 1""",
            module_name,
            revision_tag,
        )

        if not result:
            raise yam_exception.YamException(
                "Could not find module '{name}' with revision tag {tag} in "
                "database".format(name=module_name, tag=revision_tag)
            )

        assert "relid" in result
        release_id = result["relid"]
        del result

        # Get the current branches string
        yam_log.say("Getting branch for the release ID from database")
        result = self.__fetch_one("SELECT branches FROM modpkgReleases WHERE relid=%s", release_id)

        assert "branches" in result
        branches_string = result["branches"]

        # Replace full match
        if branches_string:
            branches_list = [
                re.sub("^" + branch_id + "$", new_branch_id, b.strip()) for b in branches_string.split(",")
            ]
        else:
            # should normally not get here since the branch field should
            # contain the current branch name
            branches_list = []

        try:
            # Update the cell with the new values
            yam_log.say("Updating the release ID in the database")
            self.__execute(
                "UPDATE modpkgReleases SET branches=%s WHERE relid=%s",
                ", ".join(branches_list),
                release_id,
            )
        except connector.ProgrammingError as exception:  # pragma: NO COVER
            # Write permission error. This is hackish and a leaky abstraction,
            # but we are currently using this specific method to test for
            # database writability.
            raise yam_exception.YamException(str(exception))  # pragma: NO COVER

    def write_module_source_release_information(
        self,
        module_name,
        revision_tag,
        username,
        date_time,
        changed_api_filename_list,
        readmes,
        num_files_changed,
        num_lines_added,
        num_lines_removed,
        operating_system_name,
        site_name,
        host_ip,
        release_path,
        maintenance_name,
        maintenance_num,
    ):
        """SQL implementation of write_module_source_release_information().

        username, num_lines_changed, num_lines_added, num_lines_removed,
        operating_system_name, host_ip, site_name, and release_path are
        used by some webpage.

        """
        module_name = name_utils.filter_module_name(module_name)

        incremented_num_releases = self.__num_releases(module_name=module_name) + 1

        # Construct a dictionary with the information we will add as a
        # row trim the api changes string length if necessary. Max
        # allowed is 64K, and something is quite wrong if we get
        # anywhere close to this size
        MAX_API_CHANGES_LEN = 200
        info = {
            "modpkgId": self.__module_id(module_name=module_name),
            "tag": revision_tag,
            "user": username,
            "datetime": date_time,
            # Old yam uses this value, which I assume means that the module
            # previously exists.
            "existing": "TRUE",
            "relnum": incremented_num_releases,
            "apiChangedFiles": ",".join(changed_api_filename_list)[:MAX_API_CHANGES_LEN],
            "readmes": ", ".join(readmes),
            # TODO: Figure out how to get the number of packages that
            #       depend on this module.
            "nrelatives": 0,
            "filesChanged": max(0, num_files_changed),
            "addedLOC": max(0, num_lines_added),
            "removedLOC": max(0, num_lines_removed),
            # This doesn't seem to be used anymore. The column in the
            # current database is filled with zeroes.
            "changedLOC": 0,
            "overallLOC": max(0, num_lines_added + num_lines_removed),
            "type": "SOURCE",
            "yamNative": self.__operating_system_id(operating_system_name=operating_system_name),
            "site": self.__site_id(site_name=site_name),
            "host": self.__host_id(host_ip=host_ip),
            "path": self.__release_path_id(release_path=release_path),
        }

        if maintenance_name:
            # sptag = revision_tag.split('-')
            # info['tag'] = sptag[0] + '-' + sptag[1]
            info["type"] = "MAINTSOURCE"
            info["maintBranch"] = maintenance_name
            info["maintNum"] = str(maintenance_num)

        ## print('INFO', info)

        # Construct the statement. Only directly place our keys into the
        # string. Doing the same with values risks SQL injection.
        statement = """
INSERT INTO modpkgReleases ({keys})
VALUES ({values})""".format(
            keys=", ".join(info), values=", ".join(["%s"] * len(info))
        )

        # Insert row.
        # new_release_id = self.__execute(statement, *info.values())
        new_release_id = self.__execute(statement, *info.values())

        # Update the modulePackages with the incremented number of releases.
        yam_log.say("Updating number of source releases for {} module in the database".format(module_name))
        self.__execute(
            """
UPDATE modulePackages
SET Nreleases=%s,latestRelid=%s, latestSourceRelid=%s
WHERE id=%s
                       """,
            incremented_num_releases,
            new_release_id,
            new_release_id,
            self.__module_id(module_name=module_name),
        )

        ## print('new_release_id=', new_release_id)
        if changed_api_filename_list:
            # print('KKK', changed_api_filename_list)
            yam_log.say(
                "Updating dependency info for the following {} API file changes".format(changed_api_filename_list)
            )
            self.__mark_dependent_module_builds_as_obsolete(
                module_name=module_name, filename_list=changed_api_filename_list
            )

        # if not release_path:
        #    self.__mark_obsolete_build(new_release_id)

    def write_module_build_release_information(
        self,
        module_name,
        revision_tag,
        build_id,
        username,
        date_time,
        readmes,
        operating_system_name,
        site_name,
        host_ip,
        release_path,
    ):
        """SQL implementation of write_module_build_release_information().

        Used in webpage: username, num_lines_changed,
        num_lines_added, num_lines_removed, operating_system_name, host_ip,
        site_name, and release_path

        """
        module_name = name_utils.filter_module_name(module_name)

        incremented_num_releases = self.__num_releases(module_name=module_name) + 1

        # Construct a dictionary with the information we will add as a row
        info = {
            "modpkgId": self.__module_id(module_name=module_name),
            "tag": revision_tag,
            "user": username,
            "datetime": date_time,
            # Old yam uses this value, which I assume means that the module
            # previously exists.
            "existing": "TRUE",
            "relnum": incremented_num_releases,
            "readmes": ", ".join(readmes),
            # TODO: Figure out how to get the number of packages that
            #       depend on this module.
            "nrelatives": 0,
            "type": "BUILD",
            "yamNative": self.__operating_system_id(operating_system_name=operating_system_name),
            "site": self.__site_id(site_name=site_name),
            "host": self.__host_id(host_ip=host_ip),
            "path": self.__release_path_id(release_path=release_path),
            "build": build_id,
        }

        # Construct the statement. Only directly place our keys into the
        # string. Doing the same with values risks SQL injection.
        statement = """
INSERT INTO modpkgReleases ({keys})
VALUES ({values})""".format(
            keys=", ".join(info), values=", ".join(["%s"] * len(info))
        )

        # Insert row.
        new_release_id = self.__execute(statement, *info.values())

        # Update the modulePackages with the incremented number of releases.
        yam_log.say("Updating number of build releases for {} module in the database".format(module_name))
        self.__execute(
            """
UPDATE modulePackages
SET Nreleases=%s, latestRelid=%s
WHERE id=%s
                       """,
            incremented_num_releases,
            new_release_id,
            self.__module_id(module_name=module_name),
        )

    def write_package_release_information(self, package_name, link_modules, revision_tag, username, date_time):
        """SQL implementation of write_package_release_information()."""
        package_name = name_utils.filter_package_name(package_name)

        incremented_num_releases = self.__num_package_releases(package_name=package_name) + 1

        # --------------------------------------
        # Construct a dictionary with the information we will add as a release row
        info = {
            "modpkgId": self.__package_id(package_name=package_name),
            "tag": revision_tag,
            "user": username,
            "datetime": date_time,
            # Old yam uses this value, which I assume means that the module
            # previously exists.
            "nrelatives": len(link_modules),
            "existing": "TRUE",
            "type": "PACKAGE",
            "relnum": incremented_num_releases,
        }

        # Construct the statement. Only directly place our keys into the
        # string. Doing the same with values risks SQL injection.
        statement = """
INSERT INTO modpkgReleases ({keys})
VALUES ({values})""".format(
            keys=", ".join(info), values=", ".join(["%s"] * len(info))
        )

        # Insert row.
        new_release_id = self.__execute(statement, *info.values())

        # --------------------------------------
        # Update the modulePackages with the incremented number of releases.
        yam_log.say("Updating number of releases for {} package in the database".format(package_name))
        self.__execute(
            """
UPDATE modulePackages
SET Nreleases=%s, latestRelid=%s, latestSourceRelid=%s
WHERE id=%s
                       """,
            incremented_num_releases,
            new_release_id,
            new_release_id,
            self.__package_id(package_name=package_name),
        )

        # --------------------------------------
        # Update the packageModuleReleases database table with entry with the
        # module relelases in this package release Also increment the
        # number of relatives count for each module in the release

        self._update_package_relatives(new_release_id, link_modules)

    def _update_package_relatives(self, pkg_relid, link_modules):
        """
        Update the packageModuleReleases database table with entry with the
        module relelases in this package release Also increment the
        number of relatives count for each module in the release
        """
        for module_name, lm_data in link_modules.items():
            # get the release id and relatives count for the link module release
            modrelid, nrelatives = self.__module_release_relatives(module_name, lm_data)
            # print('LLL', module_name, modrelid, nrelatives)
            # insert an entry in packageModuleReleases for these package/module relids
            info = {"pkgrelid": pkg_relid, "modrelid": modrelid}
            statement = """
INSERT INTO packageModuleReleases ({keys})
VALUES ({values})""".format(
                keys=", ".join(info), values=", ".join(["%s"] * len(info))
            )
            self.__execute(statement, *info.values())

            # update the relatives couunt for the module release
            # info = {'pkgrelid': new_release_id, 'modrelid': modrelid}
            self.__execute(
                """
                UPDATE modpkgReleases
                SET nrelatives=%s
                WHERE relid=%s
                """,
                nrelatives + 1,
                modrelid,
            )

    def register_new_module(self, module_name, repository_keyword, vcs_type):
        """SQL implementation of database_writer.register_new_module()."""
        module_name = name_utils.filter_module_name(module_name)
        # vcs_type = "git" if git else "svn"

        try:
            self.__module_id(module_name)
            #             dead = self.__module_is_dead(module_name)
            #             if dead:
            #                 # If the module is dead then we can overwrite it.
            #                 # Raise the appropriate exception
            #                 raise database.NonExistentModuleException(module_name)
            raise database_writer.ModuleAlreadyExistsException(module_name)
        except database.NonExistentModuleException:
            yam_log.say("Adding new {} module in the database".format(module_name))
            self.__execute(
                """
INSERT INTO modulePackages (name, type, repository, vcs)
VALUES (%s, %s, %s, %s)""",
                module_name,
                "MODULE",
                repository_keyword,
                vcs_type,
            )

    def register_new_package(self, package_name, repository_keyword, vcs_type: str = "svn"):
        """SQL implementation of database_writer.register_new_package()."""
        package_name = name_utils.filter_package_name(package_name)

        try:
            self.__package_id(package_name)
            raise database_writer.PackageAlreadyExistsException(package_name)
        except database.NonExistentPackageException:
            yam_log.say("Adding new {} package in the database".format(package_name))
            self.__execute(
                """
INSERT INTO modulePackages (name, type, repository, vcs)
VALUES (%s, %s, %s, %s)""",
                package_name,
                "PACKAGE",
                repository_keyword,
                vcs_type,
            )

    def unregister_module(self, module_name, undo=False):
        """SQL implementation of database_writer.unregister_module()."""
        yam_log.say("Removing {} module from the database".format(module_name))
        self.__execute(
            """
UPDATE modulePackages
SET description=%s
WHERE id=%s
                       """,
            "" if undo else "DEAD",
            self.__module_id(module_name),
        )

    def unregister_package(self, package_name):
        """SQL implementation of database_writer.unregister_package()."""
        yam_log.say("Removing {} package from the database".format(package_name))
        self.__execute(
            """
UPDATE modulePackages
SET description='DEAD'
WHERE id=%s
                       """,
            self.__package_id(package_name),
        )

    def initialize_database(self):
        """SQL implementation of database_writer.initialize_database()."""
        for command in _TABLE_CREATION_COMMAND_TUPLE:
            try:
                self.__execute(command)
            except connector.ProgrammingError as exception:
                raise database_writer.DatabaseAlreadyInitializedException(str(exception))
            except connector.OperationalError as exception:  # pragma: NO COVER
                raise database.ConnectionException(str(exception))  # pragma: NO COVER

    def write_build_dependencies(self, module_name, dependency_dictionary):
        """SQL implementation of database_writer.write_build_dependencies()."""
        module_id = self.__module_id(module_name=module_name)

        # Clear out old dependency information for module before filling in the
        # current dependencies.
        self.__execute("DELETE FROM moddeps WHERE modid=%s", module_id)

        for dependency, filenames in dependency_dictionary.items():
            try:
                dependency_id = self.__module_id(dependency)
                for header_filename in filenames:
                    yam_log.say(
                        "Adding {} module's ".format(module_name)
                        + " dependency on {} file to the database".format(header_filename)
                    )
                    self.__execute(
                        """INSERT INTO moddeps (modid, uses_modid, incfile)
                           VALUES (%s, %s, %s)""",
                        module_id,
                        dependency_id,
                        header_filename,
                    )
            except database.NonExistentModuleException:
                pass

    def __module_is_dead(self, module_name):
        yam_log.say("Get {} module is_dead from the database".format(module_name))
        result = self.__fetch_one(
            """SELECT description FROM modulePackages
                                              WHERE name=%s
                                              and type='MODULE'
                                              LIMIT 1
                                 """,
            module_name,
        )
        if (not result) or "description" not in result:
            raise database.NonExistentModuleException(module_name)

        return result["description"] == "DEAD"

    def __module_id(self, module_name):
        """Return the module ID, given its name."""
        yam_log.say("Get {} module id from the database".format(module_name))
        result = self.__fetch_one(
            """SELECT id FROM modulePackages
                                              WHERE name=%s
                                              and type='MODULE'
                                              LIMIT 1
                                 """,
            module_name,
        )
        if (not result) or "id" not in result:
            raise database.NonExistentModuleException(module_name)

        return result["id"]

    def __package_id(self, package_name):
        """Return the package ID, given its name."""
        yam_log.say("Get {} package id from the database".format(package_name))
        result = self.__fetch_one(
            """SELECT id FROM modulePackages
                                              WHERE name=%s
                                              and type='PACKAGE'
                                              LIMIT 1
                                 """,
            package_name,
        )
        if (not result) or "id" not in result:
            raise database.NonExistentPackageException(package_name)

        return result["id"]

    def __latest_relid_from_id(self, id):
        """Return the latest release id for the module/package given its id."""
        yam_log.say("Get {} id's latest release id from the database".format(id))
        result = self.__fetch_one(
            """SELECT relid,relnum,UNIX_TIMESTAMP(datetime) as datetime FROM modpkgReleases
                                              WHERE modpkgId=%s
                                              ORDER BY relid DESC
                                              LIMIT 1
                                 """,
            id,
        )
        if (not result) or "relid" not in result:
            raise database.NonExistentPackageException(id)

        return result["relid"], result["relnum"], result["datetime"]

    def __num_releases(self, module_name):
        """Return the module ID, given its name."""
        yam_log.say("Get number of releases for the {} module from the database".format(module_name))
        result = self.__fetch_one(
            """SELECT Nreleases FROM modulePackages
                                                     WHERE name=%s
                                                     and type='MODULE'
                                                     LIMIT 1
                                 """,
            module_name,
        )
        assert result
        assert "Nreleases" in result
        return result["Nreleases"]

    def __module_release_relatives(self, module_name, lm_data):
        """
        Return the database (release id, nrelatives) for this
        specific module release defined by the tuple of (module_name, build,
        maintenance branch, maintenance id).
        """
        yam_log.say(
            "Get release id and nrelatives for the {} module {} release from the database".format(module_name, lm_data)
        )
        # print("MMM", module_name, lm_data)
        tag, build, maintenance_br, maintenance_id = lm_data

        expr = ""
        if build:
            expr += " and build=%s " % build
        if maintenance_br:
            expr += ' and maintBranch="%s" ' % maintenance_br
            if maintenance_id:
                expr += " and maintNum=%d " % int(maintenance_id)

        result = self.__fetch_one(
            """SELECT relid,nrelatives FROM modpkgReleases,modulePackages
                                                     WHERE name=%s
                                                     and tag=%s
                                                     and modpkgReleases.modpkgId=modulePackages.id
                                                     and modulePackages.type='MODULE'
            """
            + expr
            + " LIMIT 1",
            module_name,
            tag,
        )
        assert result
        return (result["relid"], result["nrelatives"])

    def populate_package_relatives(self, pkg_name, release_tag, link_modules):
        """SQL implementation of populate_package_relatives()."""

        yam_log.say(
            "Populating relatives info for the {} package {} release in the database".format(pkg_name, release_tag)
        )

        # get the pkg release id for this package release
        statement = """
        SELECT relid, nrelatives FROM modulePackages,modpkgReleases
        WHERE modulePackages.name=%s and modulePackages.type='PACKAGE'
        and modulePackages.id=modpkgReleases.modpkgId
        and modpkgReleases.tag=%s
        LIMIT 1
        """
        result = self.__fetch_one(statement, pkg_name, release_tag)
        assert result
        pkg_relid = result["relid"]
        nrelatives = result["nrelatives"]
        # print('FFF', pkg_relid, nrelatives)

        # update the package release if the nrelatives is wrong
        if nrelatives == 0:
            yam_log.say(
                "Updating {} nrelatives value for the {} package {} release in the database".format(
                    nrelatives, pkg_name, release_tag
                )
            )
            self.__execute("UPDATE modpkgReleases SET nrelatives=%s WHERE relid=%s", len(link_modules), pkg_relid)

        # update the relatives info for this package release
        self._update_package_relatives(pkg_relid, link_modules)

    def __num_package_releases(self, package_name):
        """Return the package ID, given its name."""
        yam_log.say("Get number of releases for the {} package from the database".format(package_name))
        result = self.__fetch_one(
            """SELECT Nreleases FROM modulePackages
                                                     WHERE name=%s
                                                     and type='PACKAGE'
                                                     LIMIT 1
                                 """,
            package_name,
        )
        assert result
        assert "Nreleases" in result
        return result["Nreleases"]

    def __operating_system_id(self, operating_system_name):
        """Return the operating system ID.

        Create a row for it with a new ID if does not yet exist.

        """
        return self.__retrieve_id(table="yamNative", column="native", value=operating_system_name)

    def __host_id(self, host_ip):
        """Return the host ID.

        Create a row for it with a new ID if does not yet exist.

        """
        return self.__retrieve_id(table="hostMachine", column="host", value=host_ip)

    def __site_id(self, site_name):
        """Return the ID for the given site_name.

        Create a new row for it if it does not yet exist in the
        database.

        """
        return self.__retrieve_id(table="yamSite", column="site", value=site_name)

    def __release_path_id(self, release_path):
        """Return the release path ID.

        Create a new ID for it in the database if does not yet exist.

        """
        return self.__retrieve_id(table="releasesPath", column="path", value=release_path)

    def __retrieve_id(self, table, column, value):
        """Return the ID for the given value in the given column.

        Create a new ID for it in the database if does not yet exist.

        """
        yam_log.say(
            "Getting {value} for {table}/{column} from the database".format(table=table, column=column, value=value)
        )
        result = self.__fetch_one(
            """
SELECT id FROM {table}
WHERE {column}=%s LIMIT 1""".format(
                table=table, column=column
            ),
            value,
        )

        if result:
            return result["id"]
        else:
            return self.__execute(
                """
INSERT INTO {table} ({column})
VALUES (%s)""".format(
                    table=table, column=column
                ),
                value,
            )

    def __mark_dependent_module_builds_as_obsolete(self, module_name, filename_list):
        """Mark dependent modules builds as obsolete.

        This include module builds that depend on any of the files in
        filename_list in module_name as needing to be rebuilt.

        """

        # get the current time stamp
        module_id = self.__module_id(module_name=module_name)
        modrelid, relnum, curr_timestamp = self.__latest_relid_from_id(module_id)

        # -------------------------------------------
        # TODO: Update the "obsoleteRels" table

        # get the relid and time stamp for the previous release of
        # module_name. Any releases of user module that uses the API
        # change files are obsolete.
        statement = """
           SELECT modpkgReleases.relid, relnum,
	        UNIX_TIMESTAMP(datetime) as datetime
	        FROM modpkgReleases
		WHERE modpkgId=%s and
                relnum=%s
		LIMIT 1
        """
        result = self.__fetch_one(statement, module_id, relnum - 1)
        prev_relid = result["relid"]
        prev_timestamp = result["datetime"]

        yam_log.say("Previous {} module release was at {}".format(module_name, prev_timestamp))

        # get a dictionary with the api files impacting each of the
        # dependent modules
        dependency_dict = self.__dependent_modules_info(module_name=module_name, filename_list=filename_list)

        yam_log.say("Dependency dictionary is {}".format(dependency_dict))

        # get a dictionary with the releases to be obsoleted for each of
        # the dependent modules. These are all the releases since the
        # previous API module release. If there are none, then the
        # latest module release for the dependent module
        # dependent_module_release_ids = \
        #    self.__dependent_module_release_ids(dependency_dict.keys())

        # for each obsoleted release add an entry into the obsoleteRels
        # file consisting of the obsolete relid, the api module release
        # id, and the list of changed API files
        dep_mod_ids = dependency_dict.keys()
        for dep_mod_id in dep_mod_ids:
            # for dep_mod_id, dep_relids in dependent_module_release_ids.items():
            filenames = dependency_dict[dep_mod_id]
            filenames_str = ",".join(filenames)

            yam_log.say("Obsolete module id {}, api change files {}".format(dep_mod_id, filenames))

            # get the list of dependent module release ids that should
            # be marked as obsolte. These are any releases since the
            # timestamp, and if none, then the lates dep module release id
            dep_rel_ids = self.__dependent_module_release_ids(dep_mod_id, curr_timestamp, prev_timestamp)
            for dep_relid in dep_rel_ids:
                yam_log.say("Marking release id {} obsolete, api change file {}".format(dep_relid, filenames))

                # insert an entry in obsoleteRels table
                info = {"apirelid": modrelid, "obsrelid": dep_relid, "incfile": filenames_str}

                statement = """INSERT INTO obsoleteRels
	             ({keys})
	             VALUES  ({values})
                """.format(
                    keys=", ".join(info), values=", ".join(["%s"] * len(info))
                )
                self.__execute(statement, *info.values())  # , modrelid, dep_relid, filenames_str)

                # set the obsoletionCount for this obsoleted release
                self.__mark_obsolete_build(dep_relid)

        # -------------------------------------------

        # set the obsoletionCount for each obsoleted release
        # for dependent_release_id in dependent_module_release_ids:
        #    self.__mark_obsolete_build(dependent_release_id)

    def __mark_obsolete_build(self, release_id):
        """Mark module release as an obsolete build."""

        # add an entry in obsoleteRels table for all releases made obsolete

        # use the obsoletetRels table entries to get the number of file
        # changes making this release obsolete

        result = self.__fetch_one(
            """SELECT
                                          COUNT(obsoleteRels.obsrelid) as numrels
                                          FROM obsoleteRels
                                          WHERE obsoleteRels.obsrelid=%s
                                          GROUP BY obsoleteRels.obsrelid
                                """,
            release_id,
        )
        assert result and "numrels" in result
        numrels = result["numrels"]

        yam_log.say("Setting release id {} obsolete count to {}".format(release_id, numrels))

        # update the obsoletion count values in the modpkgReleases table
        # for this release with the new value
        self.__execute(
            "UPDATE modpkgReleases SET obsoletionCount=%s WHERE relid=%s",
            numrels,
            release_id,
        )

    def __get_dependent_modules(self, module_id, filename):
        """Return the list of dependent module ids that depend on the specified
        module's file"""
        # return the list of all dependent module ids that depend on
        # the file belonging to module_name module
        result = self.__fetch_all(
            "SELECT modid FROM moddeps WHERE uses_modid=%s and incfile=%s",
            module_id,
            filename,
        )
        # accumulate in the set of dependent modules
        file_dependent_module_ids = []
        for r in result:
            file_dependent_module_ids.append(r["modid"])

        return file_dependent_module_ids

    def __dependent_module_release_ids(self, dep_mod_id, curr_timestamp, prev_timestamp):
        """Return dependent module release IDs.

        Return the list of dependent release ids for the dependedent
        module id that has been obsoleted. The obsoleted relids are any
        release since the previous API module release time stamp. If no
        such releases were made, then latest relid is obsolete.

        """
        yam_log.say(
            "Getting module release ids for {depmodid} since {timestamp}".format(
                depmodid=dep_mod_id, timestamp=prev_timestamp
            )
        )

        # get all the release ids for the module between the previous
        # and current time stamps
        statement = """SELECT relid
		          FROM modpkgReleases
                          WHERE modpkgId=%s
		          and (UNIX_TIMESTAMP(datetime)) >=%s
		          and %s > (UNIX_TIMESTAMP(datetime))
                    """
        result = self.__fetch_all(statement, dep_mod_id, prev_timestamp, curr_timestamp)
        dependent_module_release_ids = []
        for i in result:
            dependent_module_release_ids.append(i["relid"])

        # if there were not releases, then get the latest release ID for
        # the dependent module
        if not result:
            yam_log.say("Getting latest release id")
            relid, relnum, datetime = self.__latest_relid_from_id(dep_mod_id)
            dependent_module_release_ids = [relid]

        yam_log.say("Obsolete release ids {}".format(dependent_module_release_ids))
        assert dependent_module_release_ids
        return dependent_module_release_ids

    def __dependent_modules_info(self, module_name, filename_list):
        """Return a dictionary with the list of the API files used by each of
        the dependent modules (key is the dep module id).
        """
        module_id = self.__module_id(module_name=module_name)

        # get the set of dependent module ids
        dependent_module_ids = set()
        dependency_dict = {}
        for filename in filename_list:
            yam_log.say(
                "Getting dedendent modules for {filename} in {module}".format(module=module_name, filename=filename)
                + " module repository from the database."
            )

            # return the list of all dependent module ids that depend on
            # the file belonging to module_name module
            file_dependent_module_ids = self.__get_dependent_modules(module_id, filename)

            # append dictionary entry with api files being used by each
            # dependent module
            for dep_mod_id in file_dependent_module_ids:
                if dep_mod_id not in dependency_dict:
                    dependency_dict[dep_mod_id] = []
                dependency_dict[dep_mod_id].append(filename)

        return dependency_dict

    @yam_log.function_logger("SQL-writer statement,args")
    def __execute(self, statement, *args):
        """Execute statement and return the last row ID."""
        with contextlib.closing(self.__cursor()) as cursor:
            cursor.execute(statement, args)
            return cursor.lastrowid

    @yam_log.function_logger("SQL-writer statement,args")
    def __fetch_one(self, statement, *args):
        """Execute query and return result."""
        # print('KKK', statement)
        with contextlib.closing(self.__cursor()) as cursor:
            cursor.execute(statement, args)
            return cursor.fetchone()

    @yam_log.function_logger("SQL-writer statement,args")
    def __fetch_all(self, statement, *args):
        """Execute query and return all results."""
        with contextlib.closing(self.__cursor()) as cursor:
            cursor.execute(statement, args)
            return cursor.fetchall()

    def __cursor(self):
        """Return a connection to the database."""
        try:
            if not self.__deferred_connection:
                self.__deferred_connection = connector.connect(
                    host=self.__hostname,
                    user=self.__username,
                    password=self.__password,
                    database=self.__database_name,
                    port=self.__port,
                )

            return self.__deferred_connection.cursor(cursor_class=mysql_database_utils.MySQLCursorDict)
        except (
            connector.errors.OperationalError,
            connector.errors.InterfaceError,
            connector.errors.ProgrammingError,
        ) as exception:
            raise database.ConnectionException("Could not connect to SQL database; {}".format(exception))


_TABLE_CREATION_COMMAND_TUPLE = (
    """
CREATE TABLE `hostMachine` (
  `id` smallint(5) unsigned NOT NULL auto_increment,
  `host` tinytext,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=70 DEFAULT CHARSET=latin1 AUTO_INCREMENT=70;
""",
    """
CREATE TABLE `moddeps` (
  `modid` smallint(5) unsigned default NULL,
  `uses_modid` smallint(5) unsigned default NULL,
  `incfile` tinytext,
  KEY `modid` (`modid`),
  KEY `uses_modid` (`uses_modid`),
  FULLTEXT KEY `incfile` (`incfile`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
""",
    """
CREATE TABLE `modpkgReleases` (
  `relid` mediumint(8) unsigned NOT NULL auto_increment,
  `modpkgId` smallint(5) unsigned NOT NULL default '0',
  `tag` varchar(24) NOT NULL default '',
  `relnum` mediumint(8) unsigned NOT NULL default '0',
  `datetime` datetime NOT NULL default '0000-00-00 00:00:00',
  `user` varchar(16) NOT NULL default '',
  `readmes` tinytext,
  `existing` enum('TRUE','FALSE') NOT NULL default 'FALSE',
  `nrelatives` mediumint(8) unsigned NOT NULL default '0',
  `build` varchar(16) default NULL,
  `branches` text,
  `apiChangedFiles` text,
  `type` enum('SOURCE','BUILD','PACKAGE','MAINTSOURCE','MAINTBUILD')
  default NULL,
  `obsoletionCount` mediumint(8) unsigned NOT NULL default '0',
  `site` smallint(5) unsigned NOT NULL default '1',
  `path` smallint(5) unsigned NOT NULL default '1',
  `host` smallint(5) unsigned NOT NULL default '1',
  `yamNative` smallint(5) unsigned NOT NULL default '1',
  `maintNum` varchar(4) default NULL,
  `maintBranch` varchar(255) default NULL,
  `overallLOC` mediumint(32) unsigned NOT NULL default '0',
  `filesChanged` mediumint(8) unsigned NOT NULL default '0',
  `addedLOC` mediumint(32) unsigned NOT NULL default '0',
  `removedLOC` mediumint(32) unsigned NOT NULL default '0',
  `changedLOC` mediumint(32) unsigned NOT NULL default '0',
  PRIMARY KEY  (`relid`),
  KEY `modpkgId` (`modpkgId`),
  KEY `relnum` (`relnum`),
  KEY `datetime` (`datetime`),
  KEY `user` (`user`),
  KEY `build` (`build`),
  KEY `type` (`type`),
  KEY `existing` (`existing`),
  KEY `nrelatives` (`nrelatives`),
  KEY `obsoletionCount` (`obsoletionCount`),
  KEY `tag` (`tag`),
  FULLTEXT KEY `branches` (`branches`)
) ENGINE=MyISAM AUTO_INCREMENT=18448 DEFAULT CHARSET=latin1
AUTO_INCREMENT=18448;
""",
    """
CREATE TABLE `modulePackages` (
  `id` mediumint(8) unsigned NOT NULL auto_increment,
  `name` varchar(32) character set latin1 collate latin1_bin default NULL,
  `Nreleases` mediumint(8) unsigned NOT NULL default '0',
  `type` enum('MODULE','PACKAGE') default NULL,
  `latestRelid` mediumint(8) unsigned NOT NULL default '0',
  `latestSourceRelid` mediumint(8) unsigned NOT NULL default '0',
  `description` text,
  `repository` varchar(32) default NULL,
  `external` enum('TRUE','FALSE') NOT NULL default 'FALSE',
  `obsolete` enum('TRUE','FALSE') NOT NULL default 'FALSE',
  PRIMARY KEY  (`id`),
  KEY `name` (`name`),
  KEY `obsolete` (`obsolete`),
  KEY `type` (`type`),
  KEY `latestcRelid` (`latestRelid`),
  KEY `latestSourceRelid` (`latestSourceRelid`),
  KEY `Nreleases` (`Nreleases`,`type`,`latestRelid`),
  KEY `repository` (`repository`),
  KEY `external` (`external`)
) ENGINE=MyISAM AUTO_INCREMENT=424 DEFAULT CHARSET=latin1 AUTO_INCREMENT=424;
""",
    """
CREATE TABLE `obsoleteRels` (
  `obsrelid` int(10) unsigned default NULL,
  `apirelid` int(10) unsigned default NULL,
  `incfile` tinytext,
  KEY `obsrelid` (`obsrelid`),
  KEY `apirelid` (`apirelid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
""",
    """
CREATE TABLE `packageModuleReleases` (
  `pkgrelid` mediumint(8) unsigned NOT NULL default '0',
  `modrelid` mediumint(8) unsigned NOT NULL default '0',
  KEY `pkgrelid` (`pkgrelid`),
  KEY `modrelid` (`modrelid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
""",
    """
CREATE TABLE `releaseBugIds` (
  `relid` mediumint(9) NOT NULL,
  `bugid` mediumint(9) NOT NULL,
  KEY `relid` (`relid`),
  KEY `bugid` (`bugid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
""",
    """
CREATE TABLE `releasesPath` (
  `id` smallint(5) unsigned NOT NULL auto_increment,
  `path` tinytext,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=51 DEFAULT CHARSET=latin1 AUTO_INCREMENT=51;
""",
    """
CREATE TABLE `yamNative` (
  `id` smallint(5) unsigned NOT NULL auto_increment,
  `native` tinytext,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=58 DEFAULT CHARSET=latin1 AUTO_INCREMENT=58;
""",
    """
CREATE TABLE `yamSite` (
  `id` smallint(5) unsigned NOT NULL auto_increment,
  `site` tinytext,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=50 DEFAULT CHARSET=latin1 AUTO_INCREMENT=50;
""",
    "ALTER TABLE `modulePackages` ADD COLUMN `vcs` VARCHAR(3) DEFAULT 'svn'",
)
