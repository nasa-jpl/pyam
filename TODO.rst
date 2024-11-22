================================
To-do items (sorted by priority)
================================

WARNING: this list is out of date

- Add ``config`` option to choose input/output filenames.

- Add ``config`` options to convert to tagged work modules.

- Add ``--edit`` option to ``pyam save``.

- Consider adding ``Previous`` in addition to ``Latest`` symlink to allow for
  easily finding out what has changed.

- Add global option to make released directories read-only as well. Currently
  files are only made read-only.

- Add support for maintenance releases.

    - Note that the ``MAINTBUILD`` release type is irrelevant. It makes no
      sense and is never even referenced in old yam other than in database
      table creation.

- In ``register-new-package`` check if the package definition is already in
  ``YAM.modules``. If so, give an error message.

- There should be a sanity check for cases where ``--all`` is used, but a
  module argument is still passed in.

- Check if we should be using ``make clean-links``.

- Include information from ``obsolete-builds`` in ``pyam status``.

- Add global hooks. This avoids duplication in each module. Module-specific
  hooks would override the global hook. Chaining is unnecessary as the
  module-specific hook could simply call whatever script it wants to.

- Global post-save hook. This would be useful for letting the user send the
  release notes to their bug ID database via a script. Possibly, we would
  pass the bug ID and release note message via environment variable
  (``PYAM_REVISION_TAG``, ``PYAM_MODULE_NAME``, ``PYAM_BUG_ID``).

- Add ``--email-gateway`` analogous to ``--database-gateway``.

- When saving, check SMTP connectivity early using ``SMTP.connect()``.

- Add ``-e``/``--edit`` and ``--to-main`` to ``save``.

- Allow quiting during a ``pyam setup --edit`` by prompting for confirmation.

- ``ChangeLog`` should only show those commits that were done on that module.
  Currently, if you ``svn commit`` multiple modules in one command, the
  commits from one module show up in the ``ChangeLog`` of the other modules.

- Make ``checkout`` remove/switch non-matching work module if there are no
  changes.

- While making links, manually set ``etc/SiteDefs`` to point to the appropriate
  version (if it is a link module). This is needed because the makefiles in
  SiteDefs don't seem to do this automatically sometimes for some reason.

- Add ``--revision-tag`` option to ``pyam save`` (as in ``save-package``).

- Something like git aliases.

- Add ``--no-diff`` option to ``pyam save``. This may be useful if there are large
  text files that take too long to diff.

- Add ``--export`` option to ``pyam checkout``. This would not do
  ``svn export`` instead of ``svn checkout``. This is to avoid having ``.svn``
  files scattered throughout the module.

- Add support for updating change log on ``save-package``.

- Add automatically generate a ``version`` file with it declared as Python
  (``#!/usr/bin/env python``).

- Fill in ``obsoleteRels`` table during save.

- Add ``--existing-branch`` option to ``checkout``.

- Add ``--create-branch`` option to ``checkout``.

- In ``checkout``, support converting tagged modules into branched modules.

- Use namedtuple instead (tag, branch) and (tag, build_id) tuples.

- Print branch automatically chosen by ``checkout``.

- Add tests for case where files in local directory are marked as read-only.
  Handle possible SVN exceptions due to this.

- Write script to parse and test examples in Readme. This should help prevent
  documentation rot.

- Current ``DatabaseReader`` and ``DatabaseWriter`` leak implementation
  details. The key names from the SQL implementation are used. Use a
  namedtuple.

- Test pyam end-to-end in a clean virtual machine or clean docker image. This
  includes installation, configuration, initialization, and building and saving
  modules.

- Add ``--latest`` option to checkout.

- Add ``--time`` option to ``latest`` to sort by date.

- Choose unique branch after saving with ``--to-work``. Currently, if the save
  is a build release, we risk a branch name collision.

- Check if pysvn has a ``--internal-diff`` option. When Jonathan configures his
  ``.svn`` to use a special diff program, it breaks pysvn's diff. One unusable
  fix this by ignoring the user's configuration directory.
  http://pysvn.tigris.org/ds/viewMessage.do?dsForumId=1335&dsMessageId=2651555
  This is not usable because it results in pyam ignoring the user's stored
  passwords.

- Test exception messages. Particularly BranchedWorkModule.MergeConflict.

- Use ``relative_to_dir`` option in ``pysvn.Client.diff()`` to get rid of the
  need for the path normalizing code in ``SVNRevisionControlSystem``.

- Add ``--date`` option to ``setup`` command to use modules from that specific
  date.

- Add a test case that adds source code and builds a library and binary. This
  will allow for clean up of files in SiteDefs.

- Only create useless files if ``--create-useless-files`` is set.

- Create a locking test where 100 forked pyams each make a release. They each
  merge if necessary. At the end the release tag should be incremented by
  exactly 100.

- Write a lock directory in the module's repository. There is no risk of
  deadlock since modules are saved one at a time. At any given time, the pyam
  client will only hold one lock. The directory gets removed when the releases
  is done. The other person exits pyam with a warning about someone else
  committing::

      with lock() as lock:
          # Save module here.

      @contextmanager
      def lock(self, url, timeout=100, warning_timeout=10, warning_callback=None):
          """Return lock context."""
          # ...
          try:
              lock_path = os.path.join(url, __lock_filename)
              while True:
                  try:
                      self.__client.mkdir(lock_path)
                  except pysvn.ClientError:
                      # ...
                      import time
                      time.sleep(1.)
              yield
          finally:
              self.__client.remove(lock_path)

      __lock_filename = '.__pyam_svn_lock__'

- Upgrade the yam database tables to InnoDB for transaction support. This allows
  for fine granularity atomicity. Though higher-level lock would still be needed
  for the whole system (database, revision control, file system). We may not be
  able to use InnoDB if backward compatibility with old yam is an issue.

- Allow saving tagged work modules as build releases.

- Make sure not to collide with previous build release.

- Maintenance releases seem a lot like a new module that clones the history of
  an existing module.

- Automatically commit Subversion merge metadata (in ``.`` non-recursively).

- Consider adding keyring support. The Python-based MySQL Workbench supports it.

- Automatically generate help output into ``README.rst``. Possibly use
  https://github.com/ribozz/sphinx-argparse/blob/master/sphinxarg/parser.py.

- Make password prompt clearer.

- Option to make ``sync`` only rebuild the synced modules.

- Notes from Scott Nemeth:
    - Areas of potential improvement:
        - Permission issue when creating a new module, others can not perform
          saves because the module directory in the module release directory
          does not allow group write permission (believe this is already fixed
          by Steven).
        - Package management: Required to svn commit yam.config file before
          saving package (should probably have pyam check to see it was
          committed).
    - Desired features:
        - Release builder (i.e. no svn checkout, use svn export instead).
        - Add an option for doing a dryrun module save, “pyam save –dry-run
          MODULE_NAME”, similar to the “svn merge –dry-run”.  This option could
          do all the typical checking that is performed, and also identify if
          any merge conflicts would occur.

- After converting a work module to a link module, remove the module in the
  ``src`` directory after prompting the user. Currently, we are just telling
  the user to do this themselves. The module should be checked for uncommitted
  changes.

- Default to ``~/.pyamrc`` if ``YAM_PROJECT_CONFIG_DIR`` is not defined.
