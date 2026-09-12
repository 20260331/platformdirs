Add a ``safe_paths`` option (keyword-only on the module-level functions, defaulting to ``False``) that normalizes and
validates ``appname``, ``appauthor`` and ``version`` as single safe path segments. Leading and trailing whitespace is
stripped, and values containing path separators, ``.``/``..``, Windows reserved device names (such as ``CON`` or
``NUL``), forbidden characters or trailing dots raise the new diagnostic
:class:`platformdirs.UnsafePathError` (a ``ValueError`` subclass), so untrusted identifiers from configuration files
or user input can no longer escape the platform base directory or resolve inconsistently across platforms.
