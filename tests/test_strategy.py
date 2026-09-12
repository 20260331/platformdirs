from __future__ import annotations

import dataclasses
import inspect
import os
import pwd
import sys
import types
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

import platformdirs
from platformdirs import PlatformDirStrategy
from platformdirs import android as android_module
from platformdirs.android import Android
from platformdirs.macos import MacOS
from platformdirs.strategy import detect_platform_dir_class
from platformdirs.unix import Unix
from platformdirs.windows import Windows

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_mock import MockerFixture

_ALL_FUNCTIONS = sorted(
    name
    for name in platformdirs.__all__
    if name.endswith(("_dir", "_path")) and not name.startswith(("PlatformDirs", "AppDirs"))
)

# A complete Windows environment; paths intentionally stay in Windows spelling, matching how the rules are used.
_WIN_ENV = {
    "APPDATA": r"C:\Users\Test\AppData\Roaming",
    "LOCALAPPDATA": r"C:\Users\Test\AppData\Local",
    "ALLUSERSPROFILE": r"C:\ProgramData",
    "USERPROFILE": r"C:\Users\Test",
    "PUBLIC": r"C:\Users\Public",
}


@pytest.fixture
def clean_xdg(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "XDG_DATA_HOME",
        "XDG_DATA_DIRS",
        "XDG_CONFIG_HOME",
        "XDG_CONFIG_DIRS",
        "XDG_CACHE_HOME",
        "XDG_STATE_HOME",
        "XDG_RUNTIME_DIR",
        "XDG_DOCUMENTS_DIR",
        "XDG_DOWNLOAD_DIR",
        "XDG_PICTURES_DIR",
        "XDG_VIDEOS_DIR",
        "XDG_MUSIC_DIR",
        "XDG_DESKTOP_DIR",
        "XDG_PROJECTS_DIR",
        "XDG_PUBLICSHARE_DIR",
        "XDG_TEMPLATES_DIR",
    ):
        monkeypatch.delenv(name, raising=False)


def test_strategy_is_exported() -> None:
    assert platformdirs.PlatformDirStrategy is PlatformDirStrategy
    assert "PlatformDirStrategy" in platformdirs.__all__


def test_strategy_defaults_to_auto_detection(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANDROID_DATA", raising=False)
    monkeypatch.delenv("ANDROID_ROOT", raising=False)

    strategy = PlatformDirStrategy()
    assert strategy.platform_class() is platformdirs._set_platform_dir_class()  # ruff:ignore[private-member-access]
    assert detect_platform_dir_class() is strategy.platform_class()
    assert strategy.effective_system() == sys.platform
    assert strategy.env is None
    assert strategy.uid is None


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("win32", Windows),
        ("windows", Windows),
        ("darwin", MacOS),
        ("macos", MacOS),
        ("android", Android),
        ("linux", Unix),
        ("freebsd", Unix),
        ("openbsd", Unix),
        ("netbsd", Unix),
    ],
)
def test_platform_class_by_name(name: str, expected: type) -> None:
    assert PlatformDirStrategy(platform=name).platform_class() is expected


@pytest.mark.parametrize(
    ("system", "expected"),
    [
        ("win32", Windows),
        ("darwin", MacOS),
        ("linux", Unix),
        ("freebsd", Unix),
        ("openbsd", Unix),
        ("netbsd", Unix),
    ],
)
def test_detect_by_system(system: str, expected: type) -> None:
    assert detect_platform_dir_class(system=system) is expected


def test_platform_class_by_class() -> None:
    class CustomUnix(Unix):
        pass

    assert PlatformDirStrategy(platform=CustomUnix).platform_class() is CustomUnix
    assert PlatformDirStrategy(platform=Windows).platform_class() is Windows


def test_unknown_platform_name_raises() -> None:
    with pytest.raises(ValueError, match="unknown platform"):
        PlatformDirStrategy(platform="plan9")


def test_invalid_arguments_raise() -> None:
    with pytest.raises(TypeError, match="env must be a mapping"):
        PlatformDirStrategy(env="XDG_DATA_HOME=/x")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="platform must be"):
        PlatformDirStrategy(platform=42)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="uid must be"):
        PlatformDirStrategy(uid="0")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="PlatformDirsABC subclass"):
        PlatformDirStrategy(platform=str)


def test_strategy_is_immutable() -> None:
    strategy = PlatformDirStrategy(env={"XDG_DATA_HOME": "/x"})
    with pytest.raises(dataclasses.FrozenInstanceError):
        strategy.env = {}  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        strategy.system = "win32"  # type: ignore[misc]


def test_effective_system_derived_from_rules() -> None:
    assert PlatformDirStrategy(platform="windows").effective_system() == "win32"
    assert PlatformDirStrategy(platform="macos").effective_system() == "darwin"
    assert PlatformDirStrategy(platform="android").effective_system() == "linux"
    assert PlatformDirStrategy(platform="unix").effective_system() == sys.platform
    assert PlatformDirStrategy(system="freebsd").effective_system() == "freebsd"
    assert PlatformDirStrategy(platform="windows", system="linux").effective_system() == "linux"


@pytest.mark.usefixtures("clean_xdg")
def test_env_injection_drives_unix_defaults() -> None:
    strategy = PlatformDirStrategy(env={"HOME": "/home/example"})
    dirs = Unix("MyApp", version="1.0", strategy=strategy)
    assert dirs.user_data_dir == "/home/example/.local/share/MyApp/1.0"
    assert dirs.user_config_dir == "/home/example/.config/MyApp/1.0"
    assert dirs.user_cache_dir == "/home/example/.cache/MyApp/1.0"
    assert dirs.user_state_dir == "/home/example/.local/state/MyApp/1.0"
    assert dirs.user_documents_dir == "/home/example/Documents"
    assert dirs.user_bin_dir == "/home/example/.local/bin"
    assert dirs.user_fonts_dir == "/home/example/.local/share/fonts"


@pytest.mark.usefixtures("clean_xdg")
def test_xdg_env_injection(monkeypatch: pytest.MonkeyPatch) -> None:
    # An empty process environment fails loudly if any code path ignores the injected source.
    monkeypatch.setattr(os, "environ", {})

    strategy = PlatformDirStrategy(
        env={
            "HOME": "/home/example",
            "XDG_DATA_HOME": "/xdg/data",
            "XDG_CONFIG_HOME": "/xdg/config",
            "XDG_CACHE_HOME": "/xdg/cache",
            "XDG_STATE_HOME": "/xdg/state",
            "XDG_RUNTIME_DIR": "/xdg/runtime",
        }
    )
    dirs = Unix("MyApp", strategy=strategy)
    assert dirs.user_data_dir == "/xdg/data/MyApp"
    assert dirs.user_config_dir == "/xdg/config/MyApp"
    assert dirs.user_cache_dir == "/xdg/cache/MyApp"
    assert dirs.user_state_dir == "/xdg/state/MyApp"
    assert dirs.user_log_dir == "/xdg/state/MyApp/log"
    assert dirs.user_runtime_dir == "/xdg/runtime/MyApp"
    assert dirs.site_runtime_dir == "/xdg/runtime/MyApp"
    assert dirs.user_fonts_dir == "/xdg/data/fonts"
    assert dirs.user_applications_dir == "/xdg/data/applications"


def test_xdg_multipath_env_injection() -> None:
    strategy = PlatformDirStrategy(
        env={"HOME": "/home/example", "XDG_DATA_DIRS": f"/a/share{os.pathsep}/b/share", "XDG_CONFIG_DIRS": "/a/etc"}
    )
    dirs = Unix("MyApp", multipath=True, strategy=strategy)
    assert dirs.site_data_dir == f"/a/share/MyApp{os.pathsep}/b/share/MyApp"
    assert dirs.site_config_dir == "/a/etc/MyApp"
    assert list(dirs.iter_data_dirs()) == [
        "/home/example/.local/share/MyApp",
        "/a/share/MyApp",
        "/b/share/MyApp",
    ]


@pytest.mark.usefixtures("clean_xdg")
def test_instances_do_not_pollute_each_other() -> None:
    first = PlatformDirStrategy(env={"XDG_DATA_HOME": "/first", "HOME": "/home/first"})
    second = PlatformDirStrategy(env={"XDG_DATA_HOME": "/second", "HOME": "/home/second"})
    dirs_first = Unix("MyApp", strategy=first)
    dirs_second = Unix("MyApp", strategy=second)

    assert dirs_first.user_data_dir == "/first/MyApp"
    assert dirs_second.user_data_dir == "/second/MyApp"
    # repeated access stays scoped, and sharing one strategy across instances is consistent
    assert Unix(strategy=first).user_config_dir == "/home/first/.config"
    assert dirs_first.user_data_dir == "/first/MyApp"
    assert dirs_second.user_data_dir == "/second/MyApp"
    # the process environment was never modified
    assert "XDG_DATA_HOME" not in os.environ


@pytest.mark.usefixtures("clean_xdg")
def test_strategy_env_does_not_leak_between_unrelated_calls() -> None:
    injected = PlatformDirStrategy(env={"XDG_DATA_HOME": "/only-here"})
    assert platformdirs.user_data_dir(strategy=injected) == "/only-here"
    # a later default call on the same thread sees the real environment, not the injected mapping
    assert platformdirs.user_data_dir() == Unix().user_data_dir


@pytest.mark.usefixtures("clean_xdg")
def test_uid_injection_controls_root_redirect() -> None:
    env = {"HOME": "/root", "XDG_DATA_HOME": "/custom/xdg", "XDG_RUNTIME_DIR": "/custom/runtime"}
    root = PlatformDirStrategy(platform="unix", env=env, uid=0)
    user = PlatformDirStrategy(platform="unix", env=env, uid=1000)

    root_dirs = Unix("foo", use_site_for_root=True, strategy=root)
    user_dirs = Unix("foo", use_site_for_root=True, strategy=user)

    assert root_dirs.user_data_dir == os.path.join("/usr/local/share", "foo")  # ruff:ignore[os-path-join]
    assert root_dirs.user_config_dir == os.path.join("/etc/xdg", "foo")  # ruff:ignore[os-path-join]
    assert root_dirs.user_bin_dir == "/usr/local/bin"
    assert user_dirs.user_data_dir == "/custom/xdg/foo"  # XDG var honored for non-root


def test_system_type_selects_runtime_defaults(mocker: MockerFixture) -> None:
    mocker.patch("os.access", return_value=True)
    for system, expected in (
        ("freebsd", "/var/run/user/1234"),
        ("openbsd", "/tmp/run/user/1234"),  # ruff:ignore[hardcoded-temp-file]
        ("linux", "/run/user/1234"),
    ):
        strategy = PlatformDirStrategy(platform="unix", system=system, uid=1234, env={})
        assert Unix(strategy=strategy).user_runtime_dir == f"{expected}", system
        assert Unix(strategy=strategy).site_runtime_dir == ("/var/run" if system != "linux" else "/run")


def test_temp_fallback_uses_injected_env(mocker: MockerFixture) -> None:
    mocker.patch("os.access", return_value=False)
    strategy = PlatformDirStrategy(platform="unix", system="linux", uid=1234, env={"TMPDIR": "/custom-tmp"})
    assert Unix(strategy=strategy).user_runtime_dir == "/custom-tmp/runtime-1234"


def test_windows_rules_resolve_from_injected_env() -> None:
    strategy = PlatformDirStrategy(platform="windows", env=dict(_WIN_ENV))
    dirs = Windows("MyApp", "MyCompany", version="1.0", strategy=strategy)

    local = os.path.normpath(_WIN_ENV["LOCALAPPDATA"])
    roaming = os.path.normpath(_WIN_ENV["APPDATA"])
    common = os.path.normpath(_WIN_ENV["ALLUSERSPROFILE"])
    profile = os.path.normpath(_WIN_ENV["USERPROFILE"])

    assert dirs.user_data_dir == os.path.join(local, "MyCompany", "MyApp", "1.0")  # ruff:ignore[os-path-join]
    assert Windows("MyApp", roaming=True, strategy=strategy).user_data_dir == os.path.join(  # ruff:ignore[os-path-join]
        roaming, "MyApp", "MyApp"
    )
    assert dirs.site_data_dir == os.path.join(common, "MyCompany", "MyApp", "1.0")  # ruff:ignore[os-path-join]
    assert dirs.user_cache_dir == os.path.join(  # ruff:ignore[os-path-join]
        local, "MyCompany", "MyApp", "Cache", "1.0"
    )
    assert dirs.user_documents_dir == os.path.normpath(os.path.join(profile, "Documents"))  # ruff:ignore[os-path-join]
    assert dirs.user_downloads_dir.endswith("Downloads")
    assert dirs.user_projects_dir.endswith("Projects")
    assert dirs.user_publicshare_dir == os.path.normpath(_WIN_ENV["PUBLIC"])
    assert dirs.user_runtime_dir == os.path.join(local, "Temp", "MyCompany", "MyApp", "1.0")  # ruff:ignore[os-path-join]


def test_windows_override_in_injected_env() -> None:
    env = dict(_WIN_ENV)
    env["WIN_PD_OVERRIDE_LOCAL_APPDATA"] = r"  X:\custom  "
    strategy = PlatformDirStrategy(platform="windows", env=env)
    assert Windows("MyApp", strategy=strategy).user_data_dir == os.path.join(  # ruff:ignore[os-path-join]
        r"X:\custom", "MyApp", "MyApp"
    )


def test_windows_missing_injected_env_raises_without_touching_ctypes() -> None:
    strategy = PlatformDirStrategy(platform="windows", env={"USERPROFILE": r"C:\Users\Test"})
    with pytest.raises(ValueError, match="Unset environment variable: LOCALAPPDATA"):
        Windows(strategy=strategy).user_data_dir  # ruff:ignore[useless-expression]


def test_macos_rules_with_injected_home() -> None:
    strategy = PlatformDirStrategy(platform="macos", env={"HOME": "/Users/example"})
    dirs = MacOS("MyApp", version="1.0", strategy=strategy)
    assert dirs.user_data_dir == "/Users/example/Library/Application Support/MyApp/1.0"
    assert dirs.user_cache_dir == "/Users/example/Library/Caches/MyApp/1.0"
    assert dirs.user_log_dir == "/Users/example/Library/Logs/MyApp/1.0"
    assert dirs.user_documents_dir == "/Users/example/Documents"
    assert dirs.user_videos_dir == "/Users/example/Movies"
    assert dirs.user_preference_dir == "/Users/example/Library/Preferences/MyApp/1.0"
    assert dirs.site_data_dir == "/Library/Application Support/MyApp/1.0"


def test_user_dirs_file_uses_injected_env(tmp_path: Path) -> None:
    config_dir = tmp_path / "custom_config"
    config_dir.mkdir()
    (config_dir / "user-dirs.dirs").write_text('XDG_DOCUMENTS_DIR="$HOME/MyDocs"\n')
    env = {"HOME": str(tmp_path), "XDG_CONFIG_HOME": str(config_dir)}
    dirs = Unix(strategy=PlatformDirStrategy(env=env))
    assert dirs.user_documents_dir == f"{tmp_path}/MyDocs"


@pytest.mark.parametrize(
    ("env_var", "prop", "expected"),
    [
        ("XDG_DOCUMENTS_DIR", "user_documents_dir", "/media/Documents"),
        ("XDG_DOWNLOAD_DIR", "user_downloads_dir", "/media/Downloads"),
        ("XDG_DESKTOP_DIR", "user_desktop_dir", "/media/Desktop"),
        ("XDG_MUSIC_DIR", "user_music_dir", "/media/Music"),
    ],
)
def test_xdg_media_env_injection(env_var: str, prop: str, expected: str) -> None:
    dirs = Unix(strategy=PlatformDirStrategy(env={env_var: expected}))
    assert getattr(dirs, prop) == expected


def test_macos_xdg_override_uses_injected_env() -> None:
    strategy = PlatformDirStrategy(platform="macos", env={"XDG_DATA_HOME": "/xdg/data"})
    assert MacOS("MyApp", strategy=strategy).user_data_dir == "/xdg/data/MyApp"


def test_windows_templates_and_fonts_use_injected_env() -> None:
    strategy = PlatformDirStrategy(platform="windows", env=dict(_WIN_ENV))
    dirs = Windows(strategy=strategy)
    appdata = os.path.normpath(_WIN_ENV["APPDATA"])
    local = os.path.normpath(_WIN_ENV["LOCALAPPDATA"])
    assert dirs.user_templates_dir == os.path.normpath(str(Path(appdata) / "Microsoft" / "Windows" / "Templates"))
    assert dirs.user_fonts_dir == os.path.normpath(str(Path(local) / "Microsoft" / "Windows" / "Fonts"))
    assert dirs.user_bin_dir == os.path.normpath(os.path.join(local, "Programs"))  # ruff:ignore[os-path-join]


def test_env_accepts_read_only_mapping() -> None:
    env = types.MappingProxyType({"XDG_DATA_HOME": "/frozen", "HOME": "/home/example"})
    strategy = PlatformDirStrategy(env=env)
    assert Unix("MyApp", strategy=strategy).user_data_dir == "/frozen/MyApp"


def test_expanduser_posix_fallback_uses_pwd_when_home_unset() -> None:
    dirs = Unix(strategy=PlatformDirStrategy(env={}))
    home = pwd.getpwuid(os.getuid()).pw_dir
    assert dirs.user_bin_dir == f"{home}/.local/bin"
    assert dirs._expanduser("~root") == pwd.getpwnam("root").pw_dir  # ruff:ignore[private-member-access]


def test_expanduser_windows_flavors() -> None:
    dirs = Windows(strategy=PlatformDirStrategy(platform="windows", env={"USERPROFILE": r"C:\Users\T"}))
    assert dirs._expanduser("~") == r"C:\Users\T"  # ruff:ignore[private-member-access]
    assert dirs._expanduser(r"C:\Windows") == r"C:\Windows"  # ruff:ignore[private-member-access]
    home_drive = Windows(
        strategy=PlatformDirStrategy(platform="windows", env={"HOMEDRIVE": "D:", "HOMEPATH": r"\Users\T"})
    )
    assert home_drive._expanduser("~") == r"D:\Users\T"  # ruff:ignore[private-member-access]
    assert home_drive._expanduser("~other") == r"D:\Users\other"  # ruff:ignore[private-member-access]
    no_home = Windows(strategy=PlatformDirStrategy(platform="windows", env={}))
    assert no_home._expanduser("~") == "~"  # ruff:ignore[private-member-access]


@pytest.mark.parametrize("function_name", _ALL_FUNCTIONS)
def test_every_standalone_function_accepts_strategy_and_matches_instance(function_name: str) -> None:
    strategy = PlatformDirStrategy(platform="unix", env={"HOME": "/home/example", "XDG_RUNTIME_DIR": "/run/user/1000"})
    function: Callable[..., Any] = getattr(platformdirs, function_name)
    prop_name = function_name.removesuffix("_path").removesuffix("_dir")
    suffix = function_name.rsplit("_", 1)[-1]
    prop = f"{prop_name}_{suffix}"
    instance = strategy.platform_class()(strategy=strategy)
    assert function(strategy=strategy) == getattr(instance, prop)


@pytest.mark.parametrize("function_name", _ALL_FUNCTIONS)
def test_strategy_is_keyword_only_on_functions(function_name: str) -> None:
    parameter = inspect.Signature.from_callable(getattr(platformdirs, function_name)).parameters["strategy"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is None


def test_strategy_is_keyword_only_on_class_init() -> None:
    parameter = inspect.Signature.from_callable(platformdirs.PlatformDirsABC.__init__).parameters["strategy"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is None


def test_function_without_strategy_keeps_auto_detection(monkeypatch: pytest.MonkeyPatch, func: str) -> None:
    monkeypatch.setattr(platformdirs, "PlatformDirs", Unix)
    function = getattr(platformdirs, func)
    assert function() == getattr(Unix(), func)


def test_platformdirs_class_honors_strategy() -> None:
    # PlatformDirs is the detected class alias; it honors an injected environment directly.
    strategy = PlatformDirStrategy(env={"HOME": "/home/example", "XDG_DATA_HOME": "/from-strategy"})
    dirs = platformdirs.PlatformDirs("MyApp", strategy=strategy)
    assert isinstance(dirs, platformdirs.PlatformDirs)
    assert dirs.appname == "MyApp"
    assert dirs.user_data_dir == "/from-strategy/MyApp"

    # Switching directory rules goes through the strategy-selected class (or a standalone function).
    win_strategy = PlatformDirStrategy(platform="windows", env=dict(_WIN_ENV))
    win_dirs = win_strategy.platform_class()("MyApp", strategy=win_strategy)
    assert isinstance(win_dirs, Windows)
    assert platformdirs.user_data_dir("MyApp", strategy=win_strategy) == win_dirs.user_data_dir


def test_appdirs_alias_honors_strategy() -> None:
    strategy = PlatformDirStrategy(env={"XDG_DATA_HOME": "/aliased"})
    assert isinstance(platformdirs.AppDirs(strategy=strategy), platformdirs.PlatformDirs)
    assert platformdirs.AppDirs("MyApp", strategy=strategy).user_data_dir == "/aliased/MyApp"


def test_sharing_a_strategy_across_instances_is_stable() -> None:
    strategy = PlatformDirStrategy(env={"XDG_DATA_HOME": "/shared", "XDG_CACHE_HOME": "/shared-cache"})
    instances = [Unix("MyApp", strategy=strategy) for _ in range(5)]
    assert {instance.user_data_dir for instance in instances} == {"/shared/MyApp"}
    assert {instance.user_cache_dir for instance in instances} == {"/shared-cache/MyApp"}


def test_android_auto_detection_from_injected_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(android_module, "_android_folder", lambda: "/data/user/0/com.example")
    env = {"ANDROID_DATA": "/data", "ANDROID_ROOT": "/system"}
    assert detect_platform_dir_class(env=env) is Android
    assert PlatformDirStrategy(env=env).platform_class() is Android

    env["SHELL"] = "/system/bin/sh"
    assert detect_platform_dir_class(system="linux", env=env) is Unix
