from __future__ import annotations

import json
import os
import sys
from subprocess import run  # ruff:ignore[suspicious-subprocess-import]
from typing import TYPE_CHECKING

import pytest

from platformdirs import PlatformDirs
from platformdirs.__main__ import EXIT_UNSUPPORTED, PROPS, main

if TYPE_CHECKING:
    import pathlib


def test_props_same_as_test(props: tuple[str, ...]) -> None:
    assert props == PROPS


def _run_module(*args: str, env: dict[str, str] | None = None) -> tuple[int, str, str]:
    result = run(
        [sys.executable, "-m", "platformdirs", *args],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def test_run_as_module_prints_full_set(props: tuple[str, ...]) -> None:
    code, out, err = _run_module()

    assert code == 0
    assert not err
    assert "-- platformdirs" not in out  # the human-facing version banner is gone
    lines = out.splitlines()
    assert [line.split(": ", 1)[0] for line in lines] == list(props)


def test_default_query_is_readonly(tmp_path: pathlib.Path) -> None:
    env = {key: value for key, value in os.environ.items() if not key.startswith(("XDG_", "ANDROID_"))}
    env["HOME"] = str(tmp_path)

    code, _, err = _run_module(env=env)

    assert code == 0
    assert not err
    assert not any(tmp_path.iterdir())  # nothing gets created


def test_single_category_text_matches_api(capsys: pytest.CaptureFixture[str]) -> None:
    expected = PlatformDirs("MyApp", "MyCompany", version="1.0", ensure_exists=False).user_data_dir

    assert main(["user_data_dir", "--appname", "MyApp", "--appauthor", "MyCompany", "--version", "1.0"]) == 0
    assert capsys.readouterr().out == f"{expected}\n"


def test_full_text_matches_api(capsys: pytest.CaptureFixture[str]) -> None:
    dirs = PlatformDirs(ensure_exists=False)

    assert main([]) == 0
    out = capsys.readouterr().out

    assert out.splitlines() == [f"{prop}: {getattr(dirs, prop)}" for prop in PROPS]


def test_single_category_json_matches_api(capsys: pytest.CaptureFixture[str]) -> None:
    expected = PlatformDirs(ensure_exists=False).site_cache_dir

    assert main(["site_cache_dir", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out) == {"site_cache_dir": expected}


def test_full_json_is_stable_and_matches_api(capsys: pytest.CaptureFixture[str]) -> None:
    dirs = PlatformDirs(ensure_exists=False)

    assert main(["-f", "json"]) == 0
    out = capsys.readouterr().out
    parsed = json.loads(out)

    assert list(parsed) == list(PROPS)  # stable key order
    assert parsed == {prop: getattr(dirs, prop) for prop in PROPS}
    assert out.endswith("\n")


def test_app_identity_and_no_appauthor(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    class StubDirs:
        def __init__(self, **kwargs: object) -> None:
            seen.update(kwargs)

        @property
        def user_data_dir(self) -> str:
            return "/stub"

    monkeypatch.setattr("platformdirs.__main__.PlatformDirs", StubDirs)

    assert main(["user_data_dir", "-a", "App", "--appauthor", "Org", "--version", "2"]) == 0
    assert seen == {"appname": "App", "appauthor": "Org", "version": "2", "ensure_exists": False}
    assert capsys.readouterr().out == "/stub\n"

    assert main(["user_data_dir", "--no-appauthor"]) == 0
    assert seen["appauthor"] is False


def test_conflicting_appauthor_options_exit_2() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--appauthor", "Org", "--no-appauthor"])
    assert exc_info.value.code == 2


def test_unknown_category_exit_2() -> None:
    code, _, err = _run_module("not_a_real_dir")
    assert code == 2
    assert "invalid choice" in err


def test_unsupported_category_exit_3(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    class StubDirs:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs

        @property
        def user_data_dir(self) -> str:
            raise NotImplementedError

    monkeypatch.setattr("platformdirs.__main__.PlatformDirs", StubDirs)

    assert main(["user_data_dir"]) == EXIT_UNSUPPORTED
    captured = capsys.readouterr()
    assert not captured.out
    assert "user_data_dir" in captured.err
    assert sys.platform in captured.err
    assert "not supported" in captured.err


def test_unsupported_full_set_exit_3_without_partial_output(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    class StubDirs:
        def __init__(self, **kwargs: object) -> None:
            pass

        @property
        def user_data_dir(self) -> str:
            return "/ok"

        @property
        def user_config_dir(self) -> str:
            raise NotImplementedError

    monkeypatch.setattr("platformdirs.__main__.PlatformDirs", StubDirs)

    assert main(["--format", "json"]) == EXIT_UNSUPPORTED
    assert not capsys.readouterr().out
