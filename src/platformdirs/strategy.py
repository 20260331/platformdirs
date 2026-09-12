"""Injectable platform directory strategy.

A :class:`PlatformDirStrategy` lets applications and tests choose, without monkey-patching process-global state such as
:data:`sys.platform` or :data:`os.environ`:

1. the **system type** the directory rules run as (``system``),
2. the **environment source** the rules read from (``env``), and
3. the **directory rules** themselves, i.e. the :class:`~platformdirs.api.PlatformDirsABC` subclass to use (``platform``).

Passing no strategy (the default everywhere) keeps the historical automatic detection behavior exactly.
"""

from __future__ import annotations

import importlib
import os
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .api import PlatformDirsABC

if TYPE_CHECKING:
    from collections.abc import Mapping

#: Accepted aliases for the ``platform`` argument, mapped to their rule classes (imported lazily).
_PLATFORM_ALIASES: Mapping[str, str] = {
    "win32": "windows:Windows",
    "windows": "windows:Windows",
    "win": "windows:Windows",
    "darwin": "macos:MacOS",
    "macos": "macos:MacOS",
    "macosx": "macos:MacOS",
    "mac": "macos:MacOS",
    "android": "android:Android",
    "unix": "unix:Unix",
    "linux": "unix:Unix",
    "linux2": "unix:Unix",
    "freebsd": "unix:Unix",
    "openbsd": "unix:Unix",
    "netbsd": "unix:Unix",
    "bsd": "unix:Unix",
    "sunos": "unix:Unix",
    "solaris": "unix:Unix",
    "aix": "unix:Unix",
    "cygwin": "unix:Unix",
}


def _load_platform_class(target: str) -> type[PlatformDirsABC]:
    module_name, _, class_name = target.partition(":")
    module = importlib.import_module(f"platformdirs.{module_name}")
    result = getattr(module, class_name)
    if not isinstance(result, type) or not issubclass(result, PlatformDirsABC):  # pragma: no cover - defensive
        msg = f"{target} is not a PlatformDirsABC subclass"
        raise TypeError(msg)
    return result


def _partition_class(system: str) -> type[PlatformDirsABC]:
    """Pick the rule class for a :data:`sys.platform`-style system identifier."""
    if system == "win32":
        from .windows import Windows  # ruff:ignore[import-outside-top-level]

        return Windows
    if system == "darwin":
        from .macos import MacOS  # ruff:ignore[import-outside-top-level]

        return MacOS
    from .unix import Unix  # ruff:ignore[import-outside-top-level]

    return Unix


def detect_platform_dir_class(
    *,
    system: str | None = None,
    env: Mapping[str, str] | None = None,
) -> type[PlatformDirsABC]:
    """Detect the platform directory class, the same way the package does it at import time.

    :param system: A :data:`sys.platform`-style identifier (e.g. ``"win32"``, ``"darwin"``, ``"freebsd"``). Defaults to
        the running system when ``None``.
    :param env: Environment mapping to inspect for Android markers. Defaults to :data:`os.environ` when ``None``.

    :returns: The platform directory class matching the system and environment.

    """
    source: Mapping[str, str] = os.environ if env is None else env
    host_system = sys.platform if system is None else system

    if source.get("ANDROID_DATA") == "/data" and source.get("ANDROID_ROOT") == "/system":  # ruff:ignore[collapsible-if]
        if not (source.get("SHELL") or source.get("PREFIX")):
            from .android import _android_folder  # ruff:ignore[import-outside-top-level]

            if _android_folder() is not None:
                from .android import Android  # ruff:ignore[import-outside-top-level]

                return Android

    return _partition_class(host_system)


@dataclass(frozen=True, kw_only=True, slots=True)
class PlatformDirStrategy:
    """Selectable system type, environment source, and directory rules.

    Every field is optional; leaving all of them at their default is equivalent to the package's automatic detection.
    Strategies are immutable and hold no per-instance state, so the same strategy can be shared safely by many
    :class:`~platformdirs.PlatformDirs` instances and standalone function calls without them polluting one another.

    :param platform: The directory rules to use: either a :class:`~platformdirs.api.PlatformDirsABC` subclass
        (e.g. :class:`~platformdirs.windows.Windows`, :class:`~platformdirs.unix.Unix`) or one of the supported names
        (``"windows"``, ``"macos"``, ``"unix"``, ``"android"`` and common :data:`sys.platform` identifiers). When
        ``None`` (the default), the class is auto-detected from ``system``/``env``.
    :param env: Environment variable source read by the directory rules (XDG variables, ``LOCALAPPDATA``,
        ``WIN_PD_OVERRIDE_*``, and so on). When ``None`` (the default), the rules read the process-global
        :data:`os.environ` as usual. The strategy itself never mutates this mapping.
    :param system: The :data:`sys.platform`-style system type the rules should assume, e.g. ``"win32"``, ``"darwin"``,
        ``"linux"``, ``"freebsd"`` or ``"openbsd"``. When ``None`` (the default), the running :data:`sys.platform` is
        used, unless ``platform`` already implies a system type.
    :param uid: The user identifier the Unix rules should assume (drives ``use_site_for_root``). When ``None`` (the
        default), the real :func:`os.getuid` is consulted. Ignored by non-Unix rules.

    """

    platform: type[PlatformDirsABC] | str | None = None
    env: Mapping[str, str] | None = None
    system: str | None = None
    uid: int | None = None

    def platform_class(self) -> type[PlatformDirsABC]:
        """:returns: The directory-rule class selected by this strategy."""
        platform = self.platform
        if platform is None:
            return detect_platform_dir_class(system=self.system, env=self.env)
        if isinstance(platform, type):
            if not issubclass(platform, PlatformDirsABC):
                msg = f"platform class must be a PlatformDirsABC subclass, got {platform!r}"
                raise TypeError(msg)
            return platform
        target = _PLATFORM_ALIASES.get(platform.lower())
        if target is None:
            msg = f"unknown platform {platform!r}; expected a PlatformDirsABC subclass or one of {sorted(_PLATFORM_ALIASES)}"
            raise ValueError(msg)
        return _load_platform_class(target)

    def effective_system(self) -> str:
        """:returns: The :data:`sys.platform`-style identifier the directory rules should see."""
        if self.system is not None:
            return self.system
        if self.platform is not None:
            platform_class = self.platform_class()
            from .android import Android  # ruff:ignore[import-outside-top-level]
            from .macos import MacOS  # ruff:ignore[import-outside-top-level]
            from .windows import Windows  # ruff:ignore[import-outside-top-level]

            if issubclass(platform_class, Windows):
                return "win32"
            if issubclass(platform_class, MacOS):
                return "darwin"
            if issubclass(platform_class, Android):
                return "linux"
        return sys.platform

    def __post_init__(self) -> None:
        """Validate the strategy arguments eagerly."""
        if self.env is not None and not callable(getattr(self.env, "get", None)):
            msg = f"env must be a mapping of environment variables, got {type(self.env).__name__!r}"
            raise TypeError(msg)
        platform = self.platform
        if isinstance(platform, str):
            # Validate the name eagerly so misconfiguration fails at construction rather than on first property use.
            self.platform_class()
        elif isinstance(platform, type):
            if not issubclass(platform, PlatformDirsABC):
                msg = f"platform class must be a PlatformDirsABC subclass, got {platform!r}"
                raise TypeError(msg)
        elif platform is not None:
            msg = f"platform must be a PlatformDirsABC subclass, a platform name, or None, got {type(platform).__name__!r}"
            raise TypeError(msg)
        if self.uid is not None and not isinstance(self.uid, int):
            msg = f"uid must be an int or None, got {type(self.uid).__name__!r}"
            raise TypeError(msg)


__all__ = [
    "PlatformDirStrategy",
    "detect_platform_dir_class",
]
