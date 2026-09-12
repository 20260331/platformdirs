Add ``PlatformDirs.ensure_directories_exist`` and the module-level ``ensure_directories_exist`` to create multiple
directories in one call, reporting for each path whether it was created, already existed, or failed (with the
underlying operating-system error). Creation is safe against concurrent callers, file conflicts, permission errors,
and partial failures; with ``rollback=True`` the directories created by the call are removed on failure while
directories that already existed are never touched.
