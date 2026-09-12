"""Utilities for determining application-specific dirs.

Provides convenience functions (e.g. :func:`user_data_dir`, :func:`user_config_path`), a :data:`PlatformDirs` class that
auto-detects the current platform, and the :class:`~platformdirs.api.PlatformDirsABC` base class.

See <https://github.com/platformdirs/platformdirs> for details and usage.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .api import PlatformDirsABC
from .strategy import PlatformDirStrategy, detect_platform_dir_class
from .version import __version__
from .version import __version_tuple__ as __version_info__

if TYPE_CHECKING:
    import sys
    from pathlib import Path
    from typing import Any, Literal

    if sys.platform == "win32":
        from platformdirs.windows import Windows as _Result
    elif sys.platform == "darwin":
        from platformdirs.macos import MacOS as _Result
    else:
        from platformdirs.unix import Unix as _Result


def _set_platform_dir_class() -> type[PlatformDirsABC]:
    return detect_platform_dir_class()


def _make_dirs(
    selected_strategy: PlatformDirStrategy | None,
    **kwargs: Any,  # ruff:ignore[any-type]
) -> PlatformDirsABC:
    """Instantiate the directory-rule class selected by ``selected_strategy`` with the given application arguments."""
    dir_class = PlatformDirs if selected_strategy is None else selected_strategy.platform_class()
    return dir_class(strategy=selected_strategy, **kwargs)


if TYPE_CHECKING:
    # Work around mypy issue: https://github.com/python/mypy/issues/10962
    PlatformDirs = _Result
else:
    PlatformDirs = _set_platform_dir_class()  #: Currently active platform
AppDirs = PlatformDirs  #: Backwards compatibility with appdirs


def user_data_dir(  # ruff:ignore[too-many-arguments, too-many-positional-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    roaming: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    use_site_for_root: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> str:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param roaming: See `roaming <platformdirs.api.PlatformDirsABC.roaming>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: data directory tied to the user

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        roaming=roaming,
        ensure_exists=ensure_exists,
        use_site_for_root=use_site_for_root,
    ).user_data_dir


def site_data_dir(  # ruff:ignore[too-many-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    multipath: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> str:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param multipath: See `multipath <platformdirs.api.PlatformDirsABC.multipath>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: data directory shared by users

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        multipath=multipath,
        ensure_exists=ensure_exists,
    ).site_data_dir


def user_config_dir(  # ruff:ignore[too-many-arguments, too-many-positional-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    roaming: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    use_site_for_root: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> str:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param roaming: See `roaming <platformdirs.api.PlatformDirsABC.roaming>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: config directory tied to the user

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        roaming=roaming,
        ensure_exists=ensure_exists,
        use_site_for_root=use_site_for_root,
    ).user_config_dir


def site_config_dir(  # ruff:ignore[too-many-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    multipath: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> str:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param multipath: See `multipath <platformdirs.api.PlatformDirsABC.multipath>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: config directory shared by users

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        multipath=multipath,
        ensure_exists=ensure_exists,
    ).site_config_dir


def user_cache_dir(  # ruff:ignore[too-many-arguments, too-many-positional-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    opinion: bool = True,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    use_site_for_root: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> str:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param opinion: See `opinion <platformdirs.api.PlatformDirsABC.opinion>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: cache directory tied to the user

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        opinion=opinion,
        ensure_exists=ensure_exists,
        use_site_for_root=use_site_for_root,
    ).user_cache_dir


def site_cache_dir(  # ruff:ignore[too-many-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    opinion: bool = True,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> str:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param opinion: See `opinion <platformdirs.api.PlatformDirsABC.opinion>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: cache directory shared by users

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        opinion=opinion,
        ensure_exists=ensure_exists,
    ).site_cache_dir


def user_state_dir(  # ruff:ignore[too-many-arguments, too-many-positional-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    roaming: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    use_site_for_root: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> str:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param roaming: See `roaming <platformdirs.api.PlatformDirsABC.roaming>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: state directory tied to the user

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        roaming=roaming,
        ensure_exists=ensure_exists,
        use_site_for_root=use_site_for_root,
    ).user_state_dir


def site_state_dir(
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> str:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: state directory shared by users

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        ensure_exists=ensure_exists,
    ).site_state_dir


def user_log_dir(  # ruff:ignore[too-many-arguments, too-many-positional-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    opinion: bool = True,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    use_site_for_root: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> str:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param opinion: See `opinion <platformdirs.api.PlatformDirsABC.opinion>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: log directory tied to the user

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        opinion=opinion,
        ensure_exists=ensure_exists,
        use_site_for_root=use_site_for_root,
    ).user_log_dir


def site_log_dir(  # ruff:ignore[too-many-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    opinion: bool = True,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> str:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param opinion: See `opinion <platformdirs.api.PlatformDirsABC.opinion>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: log directory shared by users

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        opinion=opinion,
        ensure_exists=ensure_exists,
    ).site_log_dir


def user_documents_dir(*, strategy: PlatformDirStrategy | None = None) -> str:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: documents directory tied to the user
    """
    return _make_dirs(strategy).user_documents_dir


def user_downloads_dir(*, strategy: PlatformDirStrategy | None = None) -> str:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: downloads directory tied to the user
    """
    return _make_dirs(strategy).user_downloads_dir


def user_pictures_dir(*, strategy: PlatformDirStrategy | None = None) -> str:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: pictures directory tied to the user
    """
    return _make_dirs(strategy).user_pictures_dir


def user_videos_dir(*, strategy: PlatformDirStrategy | None = None) -> str:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: videos directory tied to the user
    """
    return _make_dirs(strategy).user_videos_dir


def user_music_dir(*, strategy: PlatformDirStrategy | None = None) -> str:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: music directory tied to the user
    """
    return _make_dirs(strategy).user_music_dir


def user_desktop_dir(*, strategy: PlatformDirStrategy | None = None) -> str:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: desktop directory tied to the user
    """
    return _make_dirs(strategy).user_desktop_dir


def user_projects_dir(*, strategy: PlatformDirStrategy | None = None) -> str:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: projects directory tied to the user
    """
    return _make_dirs(strategy).user_projects_dir


def user_publicshare_dir(*, strategy: PlatformDirStrategy | None = None) -> str:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: public share directory tied to the user
    """
    return _make_dirs(strategy).user_publicshare_dir


def user_templates_dir(*, strategy: PlatformDirStrategy | None = None) -> str:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: templates directory tied to the user
    """
    return _make_dirs(strategy).user_templates_dir


def user_fonts_dir(*, strategy: PlatformDirStrategy | None = None) -> str:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: fonts directory tied to the user
    """
    return _make_dirs(strategy).user_fonts_dir


def user_preference_dir(  # ruff:ignore[too-many-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    *,
    strategy: PlatformDirStrategy | None = None,
    roaming: bool = False,
    ensure_exists: bool = False,
    use_site_for_root: bool = False,
) -> str:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param roaming: See `roaming <platformdirs.api.PlatformDirsABC.roaming>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: preference directory tied to the user

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        roaming=roaming,
        ensure_exists=ensure_exists,
        use_site_for_root=use_site_for_root,
    ).user_preference_dir


def user_bin_dir(*, strategy: PlatformDirStrategy | None = None, use_site_for_root: bool = False) -> str:
    """:param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: bin directory tied to the user

    """
    return _make_dirs(strategy, use_site_for_root=use_site_for_root).user_bin_dir


def site_bin_dir(*, strategy: PlatformDirStrategy | None = None) -> str:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: bin directory shared by users
    """
    return _make_dirs(strategy).site_bin_dir


def user_applications_dir(  # ruff:ignore[too-many-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    *,
    strategy: PlatformDirStrategy | None = None,
    ensure_exists: bool = False,
    use_site_for_root: bool = False,
) -> str:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: applications directory tied to the user

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        ensure_exists=ensure_exists,
        use_site_for_root=use_site_for_root,
    ).user_applications_dir


def site_applications_dir(  # ruff:ignore[too-many-arguments]
    multipath: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
) -> str:
    """:param multipath: See `multipath <platformdirs.api.PlatformDirsABC.multipath>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: applications directory shared by users

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        multipath=multipath,
        ensure_exists=ensure_exists,
    ).site_applications_dir


def user_runtime_dir(  # ruff:ignore[too-many-arguments, too-many-positional-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    opinion: bool = True,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    use_site_for_root: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> str:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param opinion: See `opinion <platformdirs.api.PlatformDirsABC.opinion>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: runtime directory tied to the user

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        opinion=opinion,
        ensure_exists=ensure_exists,
        use_site_for_root=use_site_for_root,
    ).user_runtime_dir


def site_runtime_dir(  # ruff:ignore[too-many-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    opinion: bool = True,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> str:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param opinion: See `opinion <platformdirs.api.PlatformDirsABC.opinion>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: runtime directory shared by users

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        opinion=opinion,
        ensure_exists=ensure_exists,
    ).site_runtime_dir


def user_data_path(  # ruff:ignore[too-many-arguments, too-many-positional-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    roaming: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    use_site_for_root: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> Path:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param roaming: See `roaming <platformdirs.api.PlatformDirsABC.roaming>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: data path tied to the user

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        roaming=roaming,
        ensure_exists=ensure_exists,
        use_site_for_root=use_site_for_root,
    ).user_data_path


def site_data_path(  # ruff:ignore[too-many-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    multipath: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> Path:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param multipath: See `multipath <platformdirs.api.PlatformDirsABC.multipath>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: data path shared by users

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        multipath=multipath,
        ensure_exists=ensure_exists,
    ).site_data_path


def user_config_path(  # ruff:ignore[too-many-arguments, too-many-positional-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    roaming: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    use_site_for_root: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> Path:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param roaming: See `roaming <platformdirs.api.PlatformDirsABC.roaming>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: config path tied to the user

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        roaming=roaming,
        ensure_exists=ensure_exists,
        use_site_for_root=use_site_for_root,
    ).user_config_path


def site_config_path(  # ruff:ignore[too-many-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    multipath: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> Path:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param multipath: See `multipath <platformdirs.api.PlatformDirsABC.multipath>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: config path shared by users

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        multipath=multipath,
        ensure_exists=ensure_exists,
    ).site_config_path


def site_cache_path(  # ruff:ignore[too-many-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    opinion: bool = True,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> Path:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param opinion: See `opinion <platformdirs.api.PlatformDirsABC.opinion>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: cache path shared by users

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        opinion=opinion,
        ensure_exists=ensure_exists,
    ).site_cache_path


def user_cache_path(  # ruff:ignore[too-many-arguments, too-many-positional-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    opinion: bool = True,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    use_site_for_root: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> Path:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param opinion: See `opinion <platformdirs.api.PlatformDirsABC.opinion>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: cache path tied to the user

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        opinion=opinion,
        ensure_exists=ensure_exists,
        use_site_for_root=use_site_for_root,
    ).user_cache_path


def user_state_path(  # ruff:ignore[too-many-arguments, too-many-positional-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    roaming: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    use_site_for_root: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> Path:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param roaming: See `roaming <platformdirs.api.PlatformDirsABC.roaming>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: state path tied to the user

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        roaming=roaming,
        ensure_exists=ensure_exists,
        use_site_for_root=use_site_for_root,
    ).user_state_path


def site_state_path(
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> Path:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: state path shared by users

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        ensure_exists=ensure_exists,
    ).site_state_path


def user_log_path(  # ruff:ignore[too-many-arguments, too-many-positional-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    opinion: bool = True,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    use_site_for_root: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> Path:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param opinion: See `opinion <platformdirs.api.PlatformDirsABC.opinion>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: log path tied to the user

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        opinion=opinion,
        ensure_exists=ensure_exists,
        use_site_for_root=use_site_for_root,
    ).user_log_path


def site_log_path(  # ruff:ignore[too-many-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    opinion: bool = True,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> Path:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param opinion: See `opinion <platformdirs.api.PlatformDirsABC.opinion>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: log path shared by users

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        opinion=opinion,
        ensure_exists=ensure_exists,
    ).site_log_path


def user_documents_path(*, strategy: PlatformDirStrategy | None = None) -> Path:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: documents path tied to the user
    """
    return _make_dirs(strategy).user_documents_path


def user_downloads_path(*, strategy: PlatformDirStrategy | None = None) -> Path:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: downloads path tied to the user
    """
    return _make_dirs(strategy).user_downloads_path


def user_pictures_path(*, strategy: PlatformDirStrategy | None = None) -> Path:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: pictures path tied to the user
    """
    return _make_dirs(strategy).user_pictures_path


def user_videos_path(*, strategy: PlatformDirStrategy | None = None) -> Path:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: videos path tied to the user
    """
    return _make_dirs(strategy).user_videos_path


def user_music_path(*, strategy: PlatformDirStrategy | None = None) -> Path:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: music path tied to the user
    """
    return _make_dirs(strategy).user_music_path


def user_desktop_path(*, strategy: PlatformDirStrategy | None = None) -> Path:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: desktop path tied to the user
    """
    return _make_dirs(strategy).user_desktop_path


def user_projects_path(*, strategy: PlatformDirStrategy | None = None) -> Path:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: projects path tied to the user
    """
    return _make_dirs(strategy).user_projects_path


def user_publicshare_path(*, strategy: PlatformDirStrategy | None = None) -> Path:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: public share path tied to the user
    """
    return _make_dirs(strategy).user_publicshare_path


def user_templates_path(*, strategy: PlatformDirStrategy | None = None) -> Path:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: templates path tied to the user
    """
    return _make_dirs(strategy).user_templates_path


def user_fonts_path(*, strategy: PlatformDirStrategy | None = None) -> Path:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: fonts path tied to the user
    """
    return _make_dirs(strategy).user_fonts_path


def user_preference_path(  # ruff:ignore[too-many-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    *,
    strategy: PlatformDirStrategy | None = None,
    roaming: bool = False,
    ensure_exists: bool = False,
    use_site_for_root: bool = False,
) -> Path:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param roaming: See `roaming <platformdirs.api.PlatformDirsABC.roaming>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: preference path tied to the user

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        roaming=roaming,
        ensure_exists=ensure_exists,
        use_site_for_root=use_site_for_root,
    ).user_preference_path


def user_bin_path(*, strategy: PlatformDirStrategy | None = None, use_site_for_root: bool = False) -> Path:
    """:param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: bin path tied to the user

    """
    return _make_dirs(strategy, use_site_for_root=use_site_for_root).user_bin_path


def site_bin_path(*, strategy: PlatformDirStrategy | None = None) -> Path:
    """:param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: bin path shared by users
    """
    return _make_dirs(strategy).site_bin_path


def user_applications_path(  # ruff:ignore[too-many-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    *,
    strategy: PlatformDirStrategy | None = None,
    ensure_exists: bool = False,
    use_site_for_root: bool = False,
) -> Path:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: applications path tied to the user

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        ensure_exists=ensure_exists,
        use_site_for_root=use_site_for_root,
    ).user_applications_path


def site_applications_path(  # ruff:ignore[too-many-arguments]
    multipath: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
) -> Path:
    """:param multipath: See `multipath <platformdirs.api.PlatformDirsABC.multipath>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: applications path shared by users

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        multipath=multipath,
        ensure_exists=ensure_exists,
    ).site_applications_path


def user_runtime_path(  # ruff:ignore[too-many-arguments, too-many-positional-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    opinion: bool = True,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    use_site_for_root: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> Path:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param opinion: See `opinion <platformdirs.api.PlatformDirsABC.opinion>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param use_site_for_root: See `use_site_for_root <platformdirs.api.PlatformDirsABC.use_site_for_root>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: runtime path tied to the user

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        opinion=opinion,
        ensure_exists=ensure_exists,
        use_site_for_root=use_site_for_root,
    ).user_runtime_path


def site_runtime_path(  # ruff:ignore[too-many-arguments]
    appname: str | None = None,
    appauthor: str | Literal[False] | None = None,
    version: str | None = None,
    opinion: bool = True,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    ensure_exists: bool = False,  # ruff:ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
    *,
    strategy: PlatformDirStrategy | None = None,
) -> Path:
    """:param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param opinion: See `opinion <platformdirs.api.PlatformDirsABC.opinion>`.
    :param ensure_exists: See `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.
    :param strategy: Optional `PlatformDirStrategy <platformdirs.strategy.PlatformDirStrategy>` choosing the system type, environment source, and directory rules; ``None`` (the default) keeps the automatic detection behavior.

    :returns: runtime path shared by users

    """
    return _make_dirs(
        strategy,
        appname=appname,
        appauthor=appauthor,
        version=version,
        opinion=opinion,
        ensure_exists=ensure_exists,
    ).site_runtime_path


__all__ = [
    "AppDirs",
    "PlatformDirStrategy",
    "PlatformDirs",
    "PlatformDirsABC",
    "__version__",
    "__version_info__",
    "site_applications_dir",
    "site_applications_path",
    "site_bin_dir",
    "site_bin_path",
    "site_cache_dir",
    "site_cache_path",
    "site_config_dir",
    "site_config_path",
    "site_data_dir",
    "site_data_path",
    "site_log_dir",
    "site_log_path",
    "site_runtime_dir",
    "site_runtime_path",
    "site_state_dir",
    "site_state_path",
    "user_applications_dir",
    "user_applications_path",
    "user_bin_dir",
    "user_bin_path",
    "user_cache_dir",
    "user_cache_path",
    "user_config_dir",
    "user_config_path",
    "user_data_dir",
    "user_data_path",
    "user_desktop_dir",
    "user_desktop_path",
    "user_documents_dir",
    "user_documents_path",
    "user_downloads_dir",
    "user_downloads_path",
    "user_fonts_dir",
    "user_fonts_path",
    "user_log_dir",
    "user_log_path",
    "user_music_dir",
    "user_music_path",
    "user_pictures_dir",
    "user_pictures_path",
    "user_preference_dir",
    "user_preference_path",
    "user_projects_dir",
    "user_projects_path",
    "user_publicshare_dir",
    "user_publicshare_path",
    "user_runtime_dir",
    "user_runtime_path",
    "user_state_dir",
    "user_state_path",
    "user_templates_dir",
    "user_templates_path",
    "user_videos_dir",
    "user_videos_path",
]
