"""Contains SQL implementation of DatabaseReader class."""

from __future__ import absolute_import

import contextlib

from mysql import connector

from . import database
from . import database_reader
from . import mysql_database_utils
from . import name_utils
from . import yam_exception
from . import yam_log


class MySQLDatabaseReader(database_reader.DatabaseReader):
    """MySQL implementation of database_reader."""

    def __init__(
        self,
        hostname,
        port,
        username,
        password,
        database_name,
        keyword_to_repository_dictionary,
    ):
        """Initialization."""
        database_reader.DatabaseReader.__init__(self)
        self.__hostname = hostname
        self.__port = port
        self.__username = username
        self.__password = password
        self.__database_name = database_name
        self.__keyword_to_repository_dictionary = keyword_to_repository_dictionary

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

    def vcs_type(self, module_name):
        """Get what type of vcs is backing this module"""
        # self._check_valid_module(module_name)
        result = self.__fetch_one(
            """SELECT vcs FROM modulePackages
                                                WHERE name = %s
                                                AND type = 'MODULE'
                                 """,
            module_name,
        )

        # return 'svn' by default for backwards compatibility
        if not result:
            return "svn"
        else:
            vcs = result["vcs"].strip()
            return vcs if vcs else "svn"

    def module_names(self):
        """SQL implementation of database_reader.module_names()."""
        yam_log.say("Getting all module names from the database")
        result = self.__fetch_all(
            """SELECT name FROM modulePackages
                                                WHERE type = 'MODULE'
                                                AND (description IS NULL OR
                                                     description != 'DEAD')
                                                ORDER BY name ASC
                                 """
        )
        return [r["name"] for r in result]

    def column_names(self, table_name):
        """Get all column of a table, for debugging purposes"""
        print("COLUMNS:")
        result = self.__fetch_all(
            "select COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='${table_name}'".format(
                table_name=table_name
            )
        )
        print([r["COLUMN_NAME"] for r in result])

    def package_names(self):
        """SQL implementation of database_reader.package_names()."""
        yam_log.say("Getting all package names from the database")
        result = self.__fetch_all(
            """SELECT name FROM modulePackages
                                                WHERE type = 'PACKAGE'
                                                AND (description IS NULL OR
                                                     description != 'DEAD')
                                                ORDER BY name ASC
                                 """
        )
        return [r["name"] for r in result]

    def latest_maintenance_release_num(self, module_name, release_tag, maintenance_branch):
        """
        For a module release tag (eg. R4-52a), return the last maintenance
        release number (eg. 5) on the specified release's maintenance
        branch (eg. ProjectA). Return -1 if no maintenance releases have
        been made yet. An exception is thrown if the maintenance branch
        does not exist.

        """

        """SQL implementation of latest_module_information()."""

        self._check_valid_module(module_name)

        yam_log.say(
            "Getting latest maintenance release num for {module} module {release}/{branch} from the database".format(
                module=module_name,
                release=release_tag,
                branch=maintenance_branch,
            )
        )
        result = self.__fetch_one(
            """
SELECT maintNum
FROM modulePackages as module, modpkgReleases
WHERE module.name='{name}'
and modpkgReleases.modpkgId=module.id
and tag='{tag}'
and maintBranch='{branch}'
and (modpkgReleases.type='MAINTSOURCE')
and module.type='MODULE'
ORDER BY maintNum DESC
LIMIT 1""".format(
                name=name_utils.filter_module_name(module_name),
                tag=release_tag,
                branch=maintenance_branch,
            )
        )
        # print("DB maint result", result)
        if result:
            assert "maintNum" in result
            return int(result["maintNum"])
        else:

            # verify that the maintenance branch exists

            yam_log.say(
                "Checing whether {module} modules {release}/{branch} maintenance branch exists  from the database".format(
                    module=module_name,
                    release=release_tag,
                    branch=maintenance_branch,
                )
            )
            nresult = self.__fetch_one(
                """
    SELECT branches
    FROM modulePackages as module, modpkgReleases
    WHERE module.name='{name}'
    and modpkgReleases.modpkgId=module.id
    and tag='{tag}'
    and (modpkgReleases.type='SOURCE')
    and module.type='MODULE'
    ORDER BY maintNum DESC
    LIMIT 1""".format(
                    name=name_utils.filter_module_name(module_name),
                    tag=release_tag,
                    branch=maintenance_branch,
                )
            )
            if not nresult:
                raise database_reader.ModuleLookupException(
                    "Could not find module '{name}' maintenance branch {release}/{branch} in SQL database".format(
                        name=module_name,
                        release=release_tag,
                        branch=maintenance_branch,
                    )
                )

            # print("DB maint nresult", nresult)
            assert "branches" in nresult
            if nresult["branches"].find(maintenance_branch + "-Maintenance") >= 0:
                # no releases have been made so far on the maintenance branch
                return -1
            else:
                raise database_reader.ModuleLookupException(
                    "Could not find module '{name}' maintenance branch {release}/{branch} in SQL database".format(
                        name=module_name,
                        release=release_tag,
                        branch=maintenance_branch,
                    )
                )

    def latest_module_information_as_of(self, module_name, release=None, date=None):
        """
        For a module release (eg. R4-52s), return dictionary with information
        about a module's latest release as of certain data.

        This release was the latest as of the given date. If date==None, use the
        latest one available. The rest works exactly as
        latest_module_information():

        The dictionary contains 'tag', 'build', 'user',
        'branches' and 'datetime'.

        'tag' for example could be 'R1-01a'.
        'build' for example could be the string '03'.
        'user' is a username string.
        'branches' is a comma-separated list of branch names.
        'datetime' is a datetime object.

        """
        """SQL implementation of latest_module_information()."""

        if date is None:
            date_filter = ""
        else:
            import dateutil.parser

            date_parsed = dateutil.parser.parse(date)
            date_filter = "and (UNIX_TIMESTAMP(datetime)) < UNIX_TIMESTAMP('{}')".format(
                date_parsed.strftime("%Y-%m-%d %H:%M:%S")
            )

        if release is None:
            tag_filter = ""
        else:
            tag_filter = "and (tag='{}')".format(release)

        # print('TTTTT1 release=', module_name, release, tag_filter)
        self._check_valid_module(module_name)

        # Given revision tag "R<number>-<rest>",
        # sort by number first, then rest alphabetically.
        # Lastly we order by build ID.
        # Note that we order by (build + 0) instead of build so that we can
        # numeric rather than alphabetic order.
        yam_log.say("Getting latest release tag for {} module from the database".format(module_name))
        result = self.__fetch_one(
            """
SELECT tag, build, datetime, user, branches
FROM modulePackages as module, modpkgReleases
WHERE module.name='{}'
and modpkgReleases.modpkgId=module.id
and ((modpkgReleases.type='SOURCE') or (modpkgReleases.type='BUILD'))
and module.type='MODULE'
{}
{}
ORDER BY (REPLACE(SUBSTRING_INDEX(tag, '-', 1), 'R', '') + 0) DESC,
         SUBSTRING_INDEX(tag, '-', 2) DESC,
         (build + 0) DESC
LIMIT 1""".format(
                name_utils.filter_module_name(module_name),
                tag_filter,
                date_filter,
            )
        )

        if result:
            assert "tag" in result
            assert "build" in result
            assert "datetime" in result
            assert "user" in result
            assert "branches" in result
            return result
        else:
            if release:
                raise database_reader.ModuleLookupException(
                    "Could not find '{r}' release for '{name}' module in SQL database{date}".format(
                        name=module_name,
                        r=release,
                        date="" if date is None else " older than {}".format(date),
                    )
                )
            else:
                raise database_reader.ModuleLookupException(
                    "Could not find '{name}' module in SQL database{date}".format(
                        name=module_name,
                        date="" if date is None else " older than {}".format(date),
                    )
                )

    def latest_module_information(self, module_name, release=None):
        """
        SQL implementation of latest_module_information() for the specific
        release (eg. R4-52s). If release is None, then for the latest release.
        """
        return self.latest_module_information_as_of(module_name, release)

    def module_history(self, module_names, limit, before, after, ascending):
        """Return dictionary with information about a module's older release.

        This release was the latest as of the given date. If date==None, use the
        latest one available. The rest works exactly as
        latest_module_information():

        The dictionary contains 'tag', 'build', 'user',
        'branches' and 'datetime'.

        'tag' for example could be 'R1-01a'.
        'build' for example could be the string '03'.
        'user' is a username string.
        'branches' is a comma-separated list of branch names.
        'datetime' is a datetime object.

        """
        """SQL implementation of latest_module_information()."""
        for module_name in module_names:
            self._check_valid_module(module_name)

        for module_name in module_names:
            yam_log.say("Getting history of {} modules from the database".format(module_name))
        build_module_query = []
        for module_name in module_names:
            build_module_query.append("module.name='" + name_utils.filter_module_name(module_name) + "'")
        build_module_query = " or ".join(build_module_query)
        build_module_query = "(" + build_module_query + ")"
        if before is not True:
            build_before_query = "and modpkgReleases.datetime < '" + before + "' "
        else:
            build_before_query = ""
        if after is not True:
            build_after_query = "and modpkgReleases.datetime > '" + after + "' "
        else:
            build_after_query = ""
        if ascending:
            build_ascending_query = "ASC"
        else:
            build_ascending_query = "DESC"
        result = self.__fetch_all(
            """
SELECT name, tag, build, datetime, user
FROM modulePackages as module, modpkgReleases
WHERE {}
and modpkgReleases.modpkgId=module.id {} {}
and modpkgReleases.type='SOURCE'
and module.type='MODULE'
ORDER BY modpkgReleases.datetime {}
LIMIT {}""".format(
                build_module_query,
                build_before_query,
                build_after_query,
                build_ascending_query,
                limit,
            )
        )
        for row in result:
            assert "tag" in row
            assert "build" in row
            assert "datetime" in row
            assert "user" in row
        return result

    def module_information(
        self,
        module_name,
        revision_tag,
        maintenance_branch="",
        maintenance_release="",
    ):
        """SQL implementation of database_reader.module_information()."""
        self._check_valid_module(module_name)

        # print("VVVV", module_name, revision_tag, maintenance_branch,
        #      maintenance_release)

        # if a maintenance branch is specified, then we must also have a maintenance release
        if maintenance_branch:
            assert maintenance_release
            reltype = " and modpkgReleases.type='MAINTSOURCE' and maintBranch='{}' and maintNum='{}' ".format(
                maintenance_branch, int(maintenance_release)
            )
        else:
            reltype = " and ((modpkgReleases.type='SOURCE') or (modpkgReleases.type='BUILD')) "

        # Given revision tag "R<number>-<rest>",
        # sort by number first, then rest alphabetically.
        # Lastly we order by build ID.
        # Note that we order by (build + 0) instead of build so that we can
        # numeric rather than alphabetic order.
        yam_log.say("Getting module release info for {} module from the database".format(module_name))
        result = self.__fetch_one(
            """
SELECT build, datetime, user, branches
FROM modulePackages as module, modpkgReleases
WHERE module.name=%s
and modpkgReleases.tag=%s
and modpkgReleases.modpkgId=module.id
"""
            + reltype
            + """
and module.type='MODULE'
ORDER BY (build + 0) DESC
LIMIT 1""",
            name_utils.filter_module_name(module_name),
            revision_tag,
        )

        if result:
            assert "build" in result
            assert "datetime" in result
            assert "user" in result
            assert "branches" in result
            return result
        else:
            raise database_reader.ModuleLookupException(
                "Could not find module '{name}-{tag}' in SQL database".format(name=module_name, tag=revision_tag)
            )

    def all_module_packages(self, type, field_order, ascending):
        """SQL implementation of all_module_packages()."""

        yam_log.say("Getting list of all {} from  the database".format(type))

        if field_order == "name":
            orderstr = " name"
        elif field_order == "nrels":
            orderstr = " Nreleases"
        elif field_order == "date":
            orderstr = " datetime"
        else:
            raise ValueError("Unknown {} sort field".format(field_order))

        orderstr += " ASC" if ascending else " DESC"

        result = self.__fetch_all(
            """
SELECT name, id, Nreleases, tag, datetime, repository,  build, maintBranch, maintNum
FROM modulePackages,modpkgReleases
WHERE modulePackages.type=%s
and modulePackages.id=modpkgReleases.modpkgId
and modulePackages.Nreleases=modpkgReleases.relnum
and obsolete='FALSE'
ORDER BY
"""
            + orderstr,
            type,
            # name_utils.filter_module_name(module_name),
            # revision_tag.strip(),
        )

        return result

    def package_release_modules(self, package_name, release_tag, field_order, ascending):
        """SQL implementation of all_module_packages()."""

        yam_log.say("Getting list of all {} from  the database".format(type))

        # get the pkg release id for this package release
        statement = """
        SELECT relid, nrelatives FROM modulePackages,modpkgReleases
        WHERE modulePackages.name=%s and modulePackages.type='PACKAGE'
        and modulePackages.id=modpkgReleases.modpkgId
        and modpkgReleases.tag=%s
        LIMIT 1
        """
        result = self.__fetch_one(statement, package_name, release_tag)
        assert result
        pkg_relid = result["relid"]
        nrelatives = result["nrelatives"]
        # print('FFF', pkg_relid, nrelatives)

        if field_order == "name":
            orderstr = " name"
        elif field_order == "nrels":
            orderstr = " Nreleases"
        elif field_order == "date":
            orderstr = " datetime"
        else:
            raise ValueError("Unknown {} sort field".format(field_order))

        orderstr += " ASC" if ascending else " DESC"

        result = self.__fetch_all(
            """
SELECT name, id, Nreleases, tag, datetime, repository, build, maintBranch, maintNum
FROM modulePackages,modpkgReleases,packageModuleReleases
WHERE modpkgReleases.modpkgId = modulePackages.id
and modpkgReleases.relid = packageModuleReleases.modrelid
and packageModuleReleases.pkgrelid=%s
ORDER BY
"""
            + orderstr,
            pkg_relid,
            # name_utils.filter_module_name(module_name),
            # revision_tag.strip(),
        )

        return result

    def all_package_releases(self):
        """
        Add info on all the package releases so far info in the database
        """

        # loop backwards through all package releases and update their relatives info

        # get all package releases
        # get the pkg release id for this package release
        statement = """
        SELECT relid, name, tag FROM modulePackages,modpkgReleases
        WHERE modulePackages.type='PACKAGE'
        and modulePackages.id=modpkgReleases.modpkgId ORDER BY relid DESC
        """
        result = self.__fetch_all(statement)
        assert result
        return result

    def has_package_relatives(self, pkg_name, release_tag):
        """SQL implementation of has_package_relatives()."""

        yam_log.say(
            "Checking for relatives info for the {} package {} release in the database".format(pkg_name, release_tag)
        )

        # check if the release info has already been populateed
        statement = """
        SELECT modpkgReleases.relid FROM packageModuleReleases,modulePackages,modpkgReleases
        WHERE modulePackages.name=%s and modulePackages.type='PACKAGE'
        and modulePackages.id=modpkgReleases.modpkgId
        and packageModuleReleases.pkgrelid=modpkgReleases.relid
        and modpkgReleases.tag=%s
        LIMIT 1
        """
        result = self.__fetch_one(statement, pkg_name, release_tag)

        return True if result else False

    def latest_package_revision_tag(self, package_name):
        """SQL implementation of latest_package_revision_tag()."""
        self._check_valid_package(package_name)

        # Given revision tag "R<number>-<rest>",
        # sort by number first, then rest alphabetically.
        yam_log.say("Getting latest release tag for {} package from the database".format(package_name))
        result = self.__fetch_one(
            """
SELECT tag
FROM modulePackages as package, modpkgReleases
WHERE package.name=%s
and modpkgReleases.modpkgId=package.id
and package.type='PACKAGE'
ORDER BY (REPLACE(SUBSTRING_INDEX(tag, '-', 1), 'R', '') + 0) DESC,
         SUBSTRING_INDEX(tag, '-', 2) DESC
LIMIT 1""",
            name_utils.filter_package_name(package_name),
        )

        if result:
            return result["tag"]
        else:
            raise database_reader.PackageLookupException(
                "Could not find package '{name}' in SQL database".format(name=package_name)
            )

    def module_repository_url(self, module_name):
        """SQL implementation of database_reader.module_repository_url()."""
        # print("MOD URL HERE")
        self._check_valid_module(module_name)

        yam_log.say("Get {} module's source repository from the database".format(module_name))
        result = self.__fetch_one(
            """
SELECT repository FROM modulePackages
WHERE type='MODULE'
and name=%s
LIMIT 1""",
            name_utils.filter_module_name(module_name),
        )

        if result:
            # print(result)
            # print("KEYWORD GOT ", self.__translate_repository_keyword(result["repository"]))
            return self.__translate_repository_keyword(result["repository"])
        else:
            raise database_reader.ModuleLookupException(
                "Could not find module '{name}' in database".format(name=module_name)
            )

    def package_repository_url(self, package_name, check_dead=True):
        """SQL implementation of database_reader.package_repository_url(). The
        check_dead option is only needed when updating missing relatives
        info for package releases in the database. This option can be
        removed once this need goes away.
        """
        if check_dead:
            self._check_valid_package(package_name)

        yam_log.say("Get {} package repository from the database".format(package_name))
        result = self.__fetch_one(
            """
SELECT repository FROM modulePackages
WHERE type='PACKAGE'
and name=%s
LIMIT 1""",
            name_utils.filter_package_name(package_name),
        )

        if result:
            return self.__translate_repository_keyword(result["repository"])
        else:
            raise database_reader.PackageLookupException(
                "Could not find package '{name}' in database".format(name=package_name)
            )

    def default_repository_url(self):
        """SQL implementation of database_reader.package_repository_url()."""
        return self.__translate_repository_keyword(None)

    def local_date_time(self):
        """SQL implementation of database_reader.local_date_time()."""
        yam_log.say("Getting date/time from the database")
        result = self.__fetch_one("SELECT NOW()")
        return result["NOW()"]

    def obsolete_builds(self):
        """SQL implementation of database_reader.obsolete_builds()."""
        obsolete_modules = set()

        for name in self.module_names():
            yam_log.say("Checking database whether {} module is obsolete".format(name))
            result = self.__fetch_one(
                """
SELECT modpkgReleases.obsoletionCount
FROM modpkgReleases, modulePackages
WHERE modpkgReleases.modpkgId = modulePackages.id
and name = %s
and modulePackages.type='MODULE'
ORDER BY relnum DESC
LIMIT 1
                                     """,
                name,
            )
            # print('LLL', name, result)

            # we should never run into a case where there is no release
            # for a module - since at least the initial one should be
            # there. But there can be cases where malformed modules may
            # have been created, so add a check here.
            if not result:
                raise ValueError(
                    'Could not find any releases for the "%s" module in the database when looking for its obsoletionCount value'
                    % name
                )

            if result and result["obsoletionCount"]:
                obsolete_modules.add(name)

        return obsolete_modules

    def module_dependencies(self, module_name):
        """SQL implementation of database_reader.module_dependencies()."""
        self._check_valid_module(module_name)

        yam_log.say("Getting {} module dependencies from the database".format(module_name))
        self._check_valid_module(module_name)
        result = self.__fetch_all(
            """
SELECT module1.name
FROM moddeps, modulePackages as module, modulePackages as module1
WHERE module.name=%s
and module.id=moddeps.modid
and module1.id=moddeps.uses_modid
GROUP BY moddeps.uses_modid
ORDER BY name ASC
           """,
            module_name,
        )
        return set([r["name"] for r in result])

    def module_dependents(self, module_name):
        """SQL implementation of database_reader.module_dependents()."""
        self._check_valid_module(module_name)

        yam_log.say("Getting {} module dependents from the database".format(module_name))
        self._check_valid_module(module_name)
        result = self.__fetch_all(
            """
SELECT module1.name
FROM moddeps, modulePackages as module, modulePackages as module1
WHERE module.name=%s
and module.id=moddeps.uses_modid
and module1.id=moddeps.modid
GROUP BY moddeps.modid
ORDER BY name ASC
""",
            module_name,
        )
        return set([r["name"] for r in result])

    def _check_valid_module(self, module_name):
        # print("CHECKING IF VALID")
        """Raise exception on bad modules."""
        yam_log.say("Checking database for {} being a valid module".format(module_name))
        result = self.__fetch_one(
            """SELECT name, description FROM modulePackages
                                                WHERE name = %s
                                                AND type = 'MODULE'
                                 """,
            module_name,
        )
        # print("RESULT: ", result)

        if not result:
            # raise yam_exception.YamException(
            raise database_reader.ModuleLookupException("Module '{module}' does not exist".format(module=module_name))

        #         result = self.__fetch_one(
        #             """SELECT name FROM modulePackages
        #                                                 WHERE name = %s
        #                                                 AND type = 'MODULE'
        #                                                 AND description = 'DEAD'
        #                                  """,
        #             module_name,
        #         )
        if result["description"] == "DEAD":
            raise database_reader.ModuleLookupException(
                # raise yam_exception.YamException(
                "Module '{module}' module is dead".format(module=module_name)
            )

    def _check_valid_package(self, package_name):
        """Raise exception on bad packages."""
        yam_log.say("Checking database for {} being a valid package".format(package_name))
        result = self.__fetch_one(
            """SELECT name, description FROM modulePackages
                                                WHERE name = %s
                                                AND type = 'PACKAGE'
                                 """,
            package_name,
        )

        if not result:
            raise database_reader.PackageLookupException(
                # raise yam_exception.YamException(
                "Package '{package}' does not exist".format(package=package_name)
            )

        #         result = self.__fetch_one(
        #             """SELECT name FROM modulePackages
        #                                                 WHERE name = %s
        #                                                 AND type = 'PACKAGE'
        #                                                 AND description = 'DEAD'
        #                                  """,
        #             package_name,
        #         )
        #         if result:
        if result["description"] == "DEAD":
            raise database_reader.PackageLookupException(
                # raise yam_exception.YamException(
                "Package '{package}' is dead".format(package=package_name)
            )

    @yam_log.function_logger("SQL-reader statement,args")
    def __fetch_one(self, statement, *args):
        """Execute query and return one result."""
        return self.__fetch(lambda x: x.fetchone(), statement, *args)

    @yam_log.function_logger("SQL-reader statement,args")
    def __fetch_all(self, statement, *args):
        """Execute query and return all results."""
        return self.__fetch(lambda x: x.fetchall(), statement, *args)

    def __fetch(self, fetcher, statement, *args):
        """Execute query and return result."""
        # Note that we use parameterized SQL to avoid injection. (Don't use
        # Python's string formatting do this!)
        with contextlib.closing(self.__cursor()) as cursor:
            try:
                cursor.execute(statement, args)
                return fetcher(cursor)
            except connector.errors.Error as exception:  # pragma: NO COVER
                raise database.ConnectionException(str(exception))  # pragma: NO COVER

    def __cursor(self):
        """Return a connection to the database."""
        try:
            # Use a buffered connection to avoid complaints about unread
            # results. This is relevant if the user sends a keyboard interrupt
            # during a read.
            if not self.__deferred_connection:
                self.__deferred_connection = connector.connect(
                    host=self.__hostname,
                    user=self.__username,
                    password=self.__password,
                    database=self.__database_name,
                    port=self.__port,
                    buffered=True,
                )

            return self.__deferred_connection.cursor(cursor_class=mysql_database_utils.MySQLCursorDict)
        except connector.errors.Error as exception:
            raise database.ConnectionException("Could not connect to database; {}".format(exception))

    def __translate_repository_keyword(self, keyword):
        """Take a repository keyword and return a repository URL."""
        try:
            # TODO: FIX THIS
            # if keyword == "git":
            #    print("DEFAULT PATH: ")
            #    print(self.__keyword_to_repository_dictionary[None])
            #    p = self.__keyword_to_repository_dictionary['DEFAULT']
            #    return p if p else self.__keyword_to_repository_dictionary[keyword]
            return self.__keyword_to_repository_dictionary[keyword]
        except KeyError:
            raise database_reader.RepositoryLookupException(
                "Could not find {k} in repository keyword to repository URL "
                "dictionary, {d}".format(k=keyword, d=self.__keyword_to_repository_dictionary)
            )
