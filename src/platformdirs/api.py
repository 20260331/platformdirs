"""Base API."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from typing import Literal


class DirectoryStatus(Enum):
    """Outcome of ensuring a single directory exists within a batch."""

    CREATED = "created"
    """The directory did not exist and was created by the call."""

    EXISTED = "existed"
    """The directory already existed (as a directory) before the call."""

    FAILED = "failed"
    """The directory could not be created; see :attr:`DirectoryCreationResult.error`."""

    ROLLED_BACK = "rolled_back"
    """The directory was created by the call, then removed again because rollback was requested and another directory
    in the batch could not be created."""


@dataclass(frozen=True)
class DirectoryCreationResult:
    """Outcome of ensuring a single directory exists within a batch."""

    path: Path
    """The directory that was requested."""

    status: DirectoryStatus
    """Whether the directory was created, already existed, failed, or was removed during rollback."""

    error: OSError | None = None
    """The operating-system error that made :attr:`status` :attr:`DirectoryStatus.FAILED`, otherwise ``None``."""


class PlatformDirsABC(ABC):  # ruff:ignore[too-many-public-methods]
    """Abstract base class defining all platform directory properties, their :class:`~pathlib.Path` variants, and iterators.

    Platform-specific subclasses (e.g. :class:`~platformdirs.windows.Windows`, :class:`~platformdirs.macos.MacOS`,
    :class:`~platformdirs.unix.Unix`) implement the abstract properties to return the appropriate paths for each
    operating system.

    """

    def __init__(  # ruff:ignore[too-many-arguments, too-many-positional-arguments]
        self,
        appname: str | None = None,
        appauthor: str | Literal[False] | None = None,
        version: str | None = None,
        roaming: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
        multipath: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
        opinion: bool = True,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
        ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
        use_site_for_root: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ) -> None:
        """Create a new platform directory.

        :param appname: See `appname`.
        :param appauthor: See `appauthor`.
        :param version: See `version`.
        :param roaming: See `roaming`.
        :param multipath: See `multipath`.
        :param opinion: See `opinion`.
        :param ensure_exists: See `ensure_exists`.
        :param use_site_for_root: See `use_site_for_root`.

        """
        self.appname = appname  #: The name of the application.
        self.appauthor = appauthor
        """The name of the app author or distributing body for this application.

        Typically, it is the owning company name. Defaults to `appname`. You may pass ``False`` to disable it.

        .. note::

            On Windows, the directory structure is ``<base>/<appauthor>/<appname>``. When ``appauthor`` is ``None`` (the
            default), it falls back to ``appname``, resulting in ``<base>/<appname>/<appname>`` (e.g.
            ``AppData/Local/myapp/myapp``). Pass ``appauthor=False`` to omit the author directory entirely and get
            ``<base>/<appname>``.

        """
        self.version = version
        """An optional version path element to append to the path.

        You might want to use this if you want multiple versions of your app to be able to run independently. If used,
        this would typically be ``<major>.<minor>``.

        """
        self.roaming = roaming
        """Whether to use the roaming appdata directory on Windows.

        That means that for users on a Windows network setup for roaming profiles, this user data will be synced on
        login (see `here <https://technet.microsoft.com/en-us/library/cc766489(WS.10).aspx>`_).

        """
        self.multipath = multipath
        """An optional parameter which indicates that the entire list of data dirs should be returned.

        By default, the first item would only be returned. Only affects ``site_data_dir`` and ``site_config_dir`` on
        Unix and macOS.

        """
        self.opinion = opinion
        """Whether to use opinionated values.

        When enabled, appends an additional subdirectory for certain directories: e.g. ``Cache`` for cache and ``Logs``
        for logs on Windows, ``log`` for logs on Unix.

        """
        self.ensure_exists = ensure_exists
        """Optionally create the directory (and any missing parents) upon access if it does not exist.

        By default, no directories are created.

        """
        self.use_site_for_root = use_site_for_root
        """Whether to redirect ``user_*_dir`` calls to their ``site_*_dir`` equivalents when running as root (uid 0).

        Only has an effect on Unix. Disabled by default for backwards compatibility. When enabled, XDG user environment
        variables (e.g. ``XDG_DATA_HOME``) are bypassed for the redirected directories.

        """

    def _append_app_name_and_version(self, *base: str) -> str:
        params = list(base[1:])
        if self.appname:
            params.append(self.appname)
            if self.version:
                params.append(self.version)
        path = os.path.join(base[0], *params)  # ruff:ignore[os-path-join]
        self._optionally_create_directory(path)
        return path

    def _optionally_create_directory(self, path: str) -> None:
        if self.ensure_exists:
            Path(path).mkdir(parents=True, exist_ok=True)

    def _first_item_as_path_if_multipath(self, directory: str) -> Path:
        if self.multipath:
            # If multipath is True, the first path is returned.
            directory = directory.partition(os.pathsep)[0]
        return Path(directory)

    @property
    @abstractmethod
    def user_data_dir(self) -> str:
        """Data directory tied to the user."""

    @property
    @abstractmethod
    def site_data_dir(self) -> str:
        """Data directory shared by users."""

    @property
    def _site_data_dirs(self) -> list[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def user_config_dir(self) -> str:
        """Config directory tied to the user."""

    @property
    @abstractmethod
    def site_config_dir(self) -> str:
        """Config directory shared by users."""

    @property
    def _site_config_dirs(self) -> list[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def user_cache_dir(self) -> str:
        """Cache directory tied to the user."""

    @property
    @abstractmethod
    def site_cache_dir(self) -> str:
        """Cache directory shared by users."""

    @property
    @abstractmethod
    def user_state_dir(self) -> str:
        """State directory tied to the user."""

    @property
    @abstractmethod
    def site_state_dir(self) -> str:
        """State directory shared by users."""

    @property
    @abstractmethod
    def user_log_dir(self) -> str:
        """Log directory tied to the user."""

    @property
    @abstractmethod
    def site_log_dir(self) -> str:
        """Log directory shared by users."""

    @property
    @abstractmethod
    def user_documents_dir(self) -> str:
        """Documents directory tied to the user."""

    @property
    @abstractmethod
    def user_downloads_dir(self) -> str:
        """Downloads directory tied to the user."""

    @property
    @abstractmethod
    def user_pictures_dir(self) -> str:
        """Pictures directory tied to the user."""

    @property
    @abstractmethod
    def user_videos_dir(self) -> str:
        """Videos directory tied to the user."""

    @property
    @abstractmethod
    def user_music_dir(self) -> str:
        """Music directory tied to the user."""

    @property
    @abstractmethod
    def user_desktop_dir(self) -> str:
        """Desktop directory tied to the user."""

    @property
    @abstractmethod
    def user_projects_dir(self) -> str:
        """Projects directory tied to the user."""

    @property
    @abstractmethod
    def user_publicshare_dir(self) -> str:
        """Public share directory tied to the user."""

    @property
    @abstractmethod
    def user_templates_dir(self) -> str:
        """Templates directory tied to the user."""

    @property
    @abstractmethod
    def user_fonts_dir(self) -> str:
        """Fonts directory tied to the user."""

    @property
    @abstractmethod
    def user_preference_dir(self) -> str:
        """Preference directory tied to the user."""

    @property
    @abstractmethod
    def user_bin_dir(self) -> str:
        """Bin directory tied to the user."""

    @property
    @abstractmethod
    def site_bin_dir(self) -> str:
        """Bin directory shared by users."""

    @property
    @abstractmethod
    def user_applications_dir(self) -> str:
        """Applications directory tied to the user."""

    @property
    @abstractmethod
    def site_applications_dir(self) -> str:
        """Applications directory shared by users."""

    @property
    def _site_applications_dirs(self) -> list[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def user_runtime_dir(self) -> str:
        """Runtime directory tied to the user."""

    @property
    @abstractmethod
    def site_runtime_dir(self) -> str:
        """Runtime directory shared by users."""

    @property
    def user_data_path(self) -> Path:
        """Data path tied to the user."""
        return Path(self.user_data_dir)

    @property
    def site_data_path(self) -> Path:
        """Data path shared by users."""
        return Path(self.site_data_dir)

    @property
    def user_config_path(self) -> Path:
        """Config path tied to the user."""
        return Path(self.user_config_dir)

    @property
    def site_config_path(self) -> Path:
        """Config path shared by users."""
        return Path(self.site_config_dir)

    @property
    def user_cache_path(self) -> Path:
        """Cache path tied to the user."""
        return Path(self.user_cache_dir)

    @property
    def site_cache_path(self) -> Path:
        """Cache path shared by users."""
        return Path(self.site_cache_dir)

    @property
    def user_state_path(self) -> Path:
        """State path tied to the user."""
        return Path(self.user_state_dir)

    @property
    def site_state_path(self) -> Path:
        """State path shared by users."""
        return Path(self.site_state_dir)

    @property
    def user_log_path(self) -> Path:
        """Log path tied to the user."""
        return Path(self.user_log_dir)

    @property
    def site_log_path(self) -> Path:
        """Log path shared by users."""
        return Path(self.site_log_dir)

    @property
    def user_documents_path(self) -> Path:
        """Documents path tied to the user."""
        return Path(self.user_documents_dir)

    @property
    def user_downloads_path(self) -> Path:
        """Downloads path tied to the user."""
        return Path(self.user_downloads_dir)

    @property
    def user_pictures_path(self) -> Path:
        """Pictures path tied to the user."""
        return Path(self.user_pictures_dir)

    @property
    def user_videos_path(self) -> Path:
        """Videos path tied to the user."""
        return Path(self.user_videos_dir)

    @property
    def user_music_path(self) -> Path:
        """Music path tied to the user."""
        return Path(self.user_music_dir)

    @property
    def user_desktop_path(self) -> Path:
        """Desktop path tied to the user."""
        return Path(self.user_desktop_dir)

    @property
    def user_projects_path(self) -> Path:
        """Projects path tied to the user."""
        return Path(self.user_projects_dir)

    @property
    def user_publicshare_path(self) -> Path:
        """Public share path tied to the user."""
        return Path(self.user_publicshare_dir)

    @property
    def user_templates_path(self) -> Path:
        """Templates path tied to the user."""
        return Path(self.user_templates_dir)

    @property
    def user_fonts_path(self) -> Path:
        """Fonts path tied to the user."""
        return Path(self.user_fonts_dir)

    @property
    def user_preference_path(self) -> Path:
        """Preference path tied to the user."""
        return Path(self.user_preference_dir)

    @property
    def user_bin_path(self) -> Path:
        """Bin path tied to the user."""
        return Path(self.user_bin_dir)

    @property
    def site_bin_path(self) -> Path:
        """Bin path shared by users."""
        return Path(self.site_bin_dir)

    @property
    def user_applications_path(self) -> Path:
        """Applications path tied to the user."""
        return Path(self.user_applications_dir)

    @property
    def site_applications_path(self) -> Path:
        """Applications path shared by users. Only return the first item, even if ``multipath`` is set to ``True``."""
        return self._first_item_as_path_if_multipath(self.site_applications_dir)

    @property
    def user_runtime_path(self) -> Path:
        """Runtime path tied to the user."""
        return Path(self.user_runtime_dir)

    @property
    def site_runtime_path(self) -> Path:
        """Runtime path shared by users."""
        return Path(self.site_runtime_dir)

    def iter_config_dirs(self) -> Iterator[str]:
        """:yield: all user and site configuration directories."""
        yield from _unique(self._iter_config_dirs())

    def _iter_config_dirs(self) -> Iterator[str]:
        yield self.user_config_dir
        yield self.site_config_dir

    def iter_data_dirs(self) -> Iterator[str]:
        """:yield: all user and site data directories."""
        yield from _unique(self._iter_data_dirs())

    def _iter_data_dirs(self) -> Iterator[str]:
        yield self.user_data_dir
        yield self.site_data_dir

    def iter_cache_dirs(self) -> Iterator[str]:
        """:yield: all user and site cache directories."""
        yield from _unique(self._iter_cache_dirs())

    def _iter_cache_dirs(self) -> Iterator[str]:
        yield self.user_cache_dir
        yield self.site_cache_dir

    def iter_state_dirs(self) -> Iterator[str]:
        """:yield: all user and site state directories."""
        yield from _unique(self._iter_state_dirs())

    def _iter_state_dirs(self) -> Iterator[str]:
        yield self.user_state_dir
        yield self.site_state_dir

    def iter_log_dirs(self) -> Iterator[str]:
        """:yield: all user and site log directories."""
        yield from _unique(self._iter_log_dirs())

    def _iter_log_dirs(self) -> Iterator[str]:
        yield self.user_log_dir
        yield self.site_log_dir

    def iter_runtime_dirs(self) -> Iterator[str]:
        """:yield: all user and site runtime directories."""
        yield from _unique(self._iter_runtime_dirs())

    def _iter_runtime_dirs(self) -> Iterator[str]:
        yield self.user_runtime_dir
        yield self.site_runtime_dir

    def iter_config_paths(self) -> Iterator[Path]:
        """:yield: all user and site configuration paths."""
        for path in self.iter_config_dirs():
            yield Path(path)

    def iter_data_paths(self) -> Iterator[Path]:
        """:yield: all user and site data paths."""
        for path in self.iter_data_dirs():
            yield Path(path)

    def iter_cache_paths(self) -> Iterator[Path]:
        """:yield: all user and site cache paths."""
        for path in self.iter_cache_dirs():
            yield Path(path)

    def iter_state_paths(self) -> Iterator[Path]:
        """:yield: all user and site state paths."""
        for path in self.iter_state_dirs():
            yield Path(path)

    def iter_log_paths(self) -> Iterator[Path]:
        """:yield: all user and site log paths."""
        for path in self.iter_log_dirs():
            yield Path(path)

    def iter_runtime_paths(self) -> Iterator[Path]:
        """:yield: all user and site runtime paths."""
        for path in self.iter_runtime_dirs():
            yield Path(path)

    def ensure_directories_exist(  # ruff:ignore[no-self-use]
        self,
        paths: Iterable[str | os.PathLike[str]],
        *,
        rollback: bool = False,
    ) -> list[DirectoryCreationResult]:
        """Ensure that several directories exist, creating missing directories (and any missing parents) as needed.

        Every requested path is attempted and reported independently, so one conflict or permission error does not
        prevent the other directories from being prepared. Directories that already existed are never modified. This
        method is safe to call concurrently from multiple threads or processes: a directory that another caller
        creates in parallel is reported as :attr:`~DirectoryStatus.EXISTED`, not created twice.

        :param paths: directories to ensure exist, given as strings or paths. Duplicate paths are handled once.
        :param rollback: when ``True``, if any directory cannot be created, remove the empty directories this call
            created, deepest first. Directories that already existed before the call, and created directories that
            are no longer empty (e.g. another process populated them), are left untouched.
        :returns: one :class:`DirectoryCreationResult` per distinct requested path, in request order.

        """
        results: list[DirectoryCreationResult] = []
        created: list[Path] = []  # Directories this call created, oldest first (no duplicates).
        seen: set[Path] = set()
        any_failed = False
        for requested in paths:
            path = Path(requested)
            if path in seen:  # A repeated path must not be reported as newly created on its second occurrence.
                continue
            seen.add(path)
            try:
                was_created = _create_directory_chain(path, created)
            except OSError as exc:
                # Parents created before the failure are already tracked in ``created``, so they are undone when
                # rollback was requested.
                results.append(DirectoryCreationResult(path=path, status=DirectoryStatus.FAILED, error=exc))
                any_failed = True
            else:
                status = DirectoryStatus.CREATED if was_created else DirectoryStatus.EXISTED
                results.append(DirectoryCreationResult(path=path, status=status))
        if rollback and any_failed:
            removed = _rollback_created(created)
            results = [
                (
                    DirectoryCreationResult(path=result.path, status=DirectoryStatus.ROLLED_BACK)
                    if result.status is DirectoryStatus.CREATED and result.path in removed
                    else result
                )
                for result in results
            ]
        return results


def _create_directory_chain(path: Path, created: list[Path]) -> bool:
    """Create ``path`` and any missing parent directories, recording each directory this call creates in ``created``.

    :returns: ``True`` when ``path`` itself was created by this call, ``False`` when it already existed as a directory.
    :raises OSError: if ``path`` exists but is not a directory, an existing ancestor is not a directory (file
        conflict), permissions prevent creation, or any other operating-system error occurs.

    """
    # Walk up only through missing nodes, then create top-down so parents exist before their children.
    missing: list[Path] = []
    node = path
    while True:
        if node.exists() or node.parent == node:
            break
        missing.append(node)
        node = node.parent

    leaf_created = False
    for node in reversed(missing):
        try:
            node.mkdir()
        except FileExistsError:
            # A concurrent caller may have won the race: a directory is exactly what we wanted, whereas a file at
            # this location is a conflict that must be reported.
            if node.is_dir():
                continue
            raise
        created.append(node)
        if node == path:
            leaf_created = True

    if not leaf_created and not path.is_dir():
        # The leaf existed before we scanned it (or appeared concurrently) and is not a directory: let mkdir raise
        # the native conflict error instead of reporting an existing file as a directory.
        path.mkdir()
    return leaf_created


def _rollback_created(created: list[Path]) -> set[Path]:
    """Remove created directories deepest first using :meth:`~pathlib.Path.rmdir`; return the paths removed.

    Only directories tracked as created by the batch are touched, and ``rmdir`` only removes empty directories, so
    pre-existing directories and directories another process has populated are left in place. Removal errors are
    ignored: leaving an empty directory behind on rollback is safer than raising while undoing a failed batch.

    """
    removed: set[Path] = set()
    for path in reversed(created):
        try:
            path.rmdir()
        except OSError:
            continue
        removed.add(path)
    return removed


def _unique(dirs: Iterable[str]) -> Iterator[str]:
    """:yield: ``dirs`` in order, skipping any directory already yielded."""
    # Lazy on purpose: under ensure_exists reading a site_*_dir creates it, so draining ``dirs`` up front would
    # create directories for a caller that stops after the first entry.
    seen: set[str] = set()
    for path in dirs:
        if path not in seen:
            seen.add(path)
            yield path
