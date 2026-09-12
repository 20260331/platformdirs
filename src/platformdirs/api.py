"""Base API."""

from __future__ import annotations

import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Mapping
    from typing import Literal

    from .strategy import PlatformDirStrategy


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
        *,
        strategy: PlatformDirStrategy | None = None,
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
        :param strategy: Optional :class:`~platformdirs.strategy.PlatformDirStrategy` selecting the system type,
            environment source, and directory rules. When ``None`` (the default), the platform and its environment are
            auto-detected as usual.

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
        self.strategy = strategy
        """Optional strategy overriding the detected system type, environment source, and directory rules.

        ``None`` means automatic detection and reads from the process-global :data:`os.environ`.

        """

    def _env_source(self) -> Mapping[str, str] | None:
        """:returns: The injected environment mapping, or ``None`` to read the process-global :data:`os.environ`."""
        if self.strategy is None:
            return None
        return self.strategy.env

    def _getenv(self, name: str) -> str | None:
        """Look up ``name`` in the injected environment source, falling back to :data:`os.environ`."""
        source = self._env_source()
        return os.environ.get(name) if source is None else source.get(name)

    def _getenv_clean(self, name: str) -> str:
        """:returns: The stripped value of ``name``, or an empty string when unset/blank."""
        value = self._getenv(name)
        return value.strip() if value is not None else ""

    def _system(self) -> str:
        """:returns: The :data:`sys.platform`-style system type the directory rules should assume."""
        if self.strategy is not None:
            return self.strategy.effective_system()
        return sys.platform

    def _expanduser(self, path: str) -> str:
        """Expand an initial ``~`` using the injected environment source, or :func:`os.path.expanduser` by default."""
        source = self._env_source()
        if source is None:
            return os.path.expanduser(path)  # ruff:ignore[os-path-expanduser]
        return _expanduser(path, source, nt=self._system() == "win32")

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


def _unique(dirs: Iterable[str]) -> Iterator[str]:
    """:yield: ``dirs`` in order, skipping any directory already yielded."""
    # Lazy on purpose: under ensure_exists reading a site_*_dir creates it, so draining ``dirs`` up front would
    # create directories for a caller that stops after the first entry.
    seen: set[str] = set()
    for path in dirs:
        if path not in seen:
            seen.add(path)
            yield path


def _expanduser(path: str, env: Mapping[str, str], *, nt: bool) -> str:
    """Expand a leading ``~`` using ``env`` instead of the process environment.

    Mirrors the relevant behavior of :func:`os.path.expanduser` so injected environments resolve home directories the
    same way the live environment would. ``nt`` selects Windows (``%USERPROFILE%``) versus POSIX (``$HOME``) rules,
    matching the selected directory rules rather than the host operating system.

    """
    if not path.startswith("~"):
        return path
    return _expanduser_nt(path, env) if nt else _expanduser_posix(path, env)


def _expanduser_posix(path: str, env: Mapping[str, str]) -> str:
    """POSIX variant of :func:`os.path.expanduser` backed by an injected mapping."""
    end = path.find("/", 1)
    if end < 0:
        end = len(path)
    name = path[1:end]
    if not name:
        home = env.get("HOME")
        if not home:
            try:
                import pwd  # ruff:ignore[import-outside-top-level]

                home = pwd.getpwuid(os.getuid()).pw_dir
            except (KeyError, ModuleNotFoundError):
                return path
        return home + path[end:]
    try:
        import pwd  # ruff:ignore[import-outside-top-level]

        home = pwd.getpwnam(name).pw_dir
    except (KeyError, ModuleNotFoundError):
        return path
    return home + path[end:]


def _expanduser_nt(path: str, env: Mapping[str, str]) -> str:
    r"""Windows variant of :func:`os.path.expanduser` backed by an injected mapping."""
    end = len(path)
    for separator in ("/", "\\"):
        index = path.find(separator, 1)
        if 0 < index < end:
            end = index
    name = path[1:end]
    if not name:
        home = env.get("USERPROFILE")
        if home is None:
            home_path = env.get("HOMEPATH")
            if home_path is None:
                return path
            home = env.get("HOMEDRIVE", "") + home_path
        return home + path[end:]
    return f"{env.get('HOMEDRIVE', 'C:')}\\Users\\{name}{path[end:]}"
