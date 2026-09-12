from __future__ import annotations

import builtins
import errno
import functools
import inspect
import os
import sys
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

import platformdirs
from platformdirs import DirectoryCreationResult, DirectoryStatus
from platformdirs.android import Android

builtin_import = builtins.__import__


if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence
    from types import ModuleType

    from pytest_mock import MockerFixture


def test_package_metadata() -> None:
    assert hasattr(platformdirs, "__version__")
    assert hasattr(platformdirs, "__version_info__")


def test_method_result_is_str(func: str) -> None:
    method = getattr(platformdirs, func)
    result = method()
    assert isinstance(result, str)


def test_property_result_is_str(func: str) -> None:
    dirs = platformdirs.PlatformDirs("MyApp", "MyCompany", version="1.0")
    result = getattr(dirs, func)
    assert isinstance(result, str)


def test_method_result_is_path(func_path: str) -> None:
    method = getattr(platformdirs, func_path)
    result = method()
    assert isinstance(result, Path)


def test_property_result_is_path(func_path: str) -> None:
    dirs = platformdirs.PlatformDirs("MyApp", "MyCompany", version="1.0")
    result = getattr(dirs, func_path)
    assert isinstance(result, Path)


def test_function_interface_is_in_sync(func: str) -> None:
    function_dir = getattr(platformdirs, func)
    function_path = getattr(platformdirs, func.replace("_dir", "_path"))
    assert inspect.isfunction(function_dir)
    assert inspect.isfunction(function_path)
    function_dir_signature = inspect.Signature.from_callable(function_dir)
    function_path_signature = inspect.Signature.from_callable(function_path)
    assert function_dir_signature.parameters == function_path_signature.parameters


@pytest.mark.parametrize("func", ["user_applications_dir", "user_applications_path"])
def test_user_applications_function_boolean_options_are_keyword_only(func: str) -> None:
    # These options have not shipped yet, so they can be keyword-only without breaking any caller.
    parameters = inspect.Signature.from_callable(getattr(platformdirs, func)).parameters
    positional = [name for name, param in parameters.items() if param.kind is param.POSITIONAL_OR_KEYWORD]
    assert positional == ["appname", "appauthor", "version"]


@pytest.mark.parametrize("func", ["site_applications_dir", "site_applications_path"])
def test_site_applications_function_keeps_multipath_positional(func: str) -> None:
    # multipath has been the first positional argument since 4.9.0, so the app arguments are keyword-only.
    parameters = inspect.Signature.from_callable(getattr(platformdirs, func)).parameters
    positional = [name for name, param in parameters.items() if param.kind is param.POSITIONAL_OR_KEYWORD]
    assert positional == ["multipath", "ensure_exists"]


def test_function_matches_its_property_for_app_arguments(func: str) -> None:
    function = getattr(platformdirs, func)
    scoped = getattr(platformdirs.PlatformDirs("MyApp", "MyCompany", version="1.0"), func)
    if {"appname", "version"} <= inspect.Signature.from_callable(function).parameters.keys():
        assert function(appname="MyApp", appauthor="MyCompany", version="1.0") == scoped
    else:
        # A function without the app arguments can only ever return the unscoped base directory, so a property that
        # is app-scoped on any platform is out of its reach. Only one direction holds: a function may have to take
        # arguments this platform ignores because another platform scopes the same property.
        assert scoped == getattr(platformdirs.PlatformDirs(), func)


@pytest.mark.parametrize("root", ["A", "/system", None])
@pytest.mark.parametrize("data", ["D", "/data", None])
@pytest.mark.parametrize("path", ["/data/data/a/files", "/C"])
@pytest.mark.parametrize("shell", ["/data/data/com.app/files/usr/bin/sh", "/usr/bin/sh", None])
@pytest.mark.parametrize("prefix", ["/data/data/com.termux/files/usr", None])
def test_android_active(  # ruff:ignore[too-many-arguments]
    monkeypatch: pytest.MonkeyPatch,
    root: str | None,
    data: str | None,
    path: str,
    shell: str | None,
    prefix: str | None,
) -> None:
    for env_var, value in {"ANDROID_DATA": data, "ANDROID_ROOT": root, "SHELL": shell, "PREFIX": prefix}.items():
        if value is None:
            monkeypatch.delenv(env_var, raising=False)
        else:
            monkeypatch.setenv(env_var, value)

    from platformdirs.android import _android_folder  # ruff:ignore[import-outside-top-level]

    _android_folder.cache_clear()
    monkeypatch.setattr(sys, "path", ["/A", "/B", path])

    expected = (
        root == "/system" and data == "/data" and shell is None and prefix is None and _android_folder() is not None
    )
    if expected:
        assert platformdirs._set_platform_dir_class() is Android  # ruff:ignore[private-member-access]
    else:
        assert platformdirs._set_platform_dir_class() is not Android  # ruff:ignore[private-member-access]


def _fake_import(
    name: str,
    globals: Mapping[str, object] | None = None,  # ruff:ignore[builtin-argument-shadowing]
    locals: Mapping[str, object] | None = None,  # ruff:ignore[builtin-argument-shadowing]
    fromlist: Sequence[str] | None = (),
    level: int = 0,
) -> ModuleType:
    if name == "ctypes":
        msg = f"No module named {name}"
        raise ModuleNotFoundError(msg)
    return builtin_import(name, globals, locals, fromlist, level)


def mock_import(func: Callable[..., None]) -> Callable[..., None]:
    @functools.wraps(func)
    def wrap(*args: Any, **kwargs: Any) -> None:  # ruff:ignore[any-type]
        platformdirs_module_items = [item for item in sys.modules.items() if item[0].startswith("platformdirs")]
        try:
            builtins.__import__ = _fake_import  # ty: ignore[invalid-assignment]
            for name, _ in platformdirs_module_items:
                del sys.modules[name]
            return func(*args, **kwargs)
        finally:
            # restore original modules
            builtins.__import__ = builtin_import
            for name, module in platformdirs_module_items:
                sys.modules[name] = module

    return wrap


@mock_import
def test_no_ctypes(func: str) -> None:
    import platformdirs  # ruff:ignore[import-outside-top-level]

    assert platformdirs

    dirs = platformdirs.PlatformDirs("MyApp", "MyCompany", version="1.0")
    result = getattr(dirs, func)
    assert isinstance(result, str)


def test_mypy_subclassing() -> None:
    # Ensure that PlatformDirs / AppDirs is seen as a valid superclass by mypy
    # This is a static type-checking test to ensure we work around
    # the following mypy issue: https://github.com/python/mypy/issues/10962
    class PlatformDirsSubclass(platformdirs.PlatformDirs): ...

    class AppDirsSubclass(platformdirs.AppDirs): ...


@pytest.mark.parametrize("kind", ["config", "data", "cache", "state", "log", "runtime"])
def test_iter_dirs_yields_user_before_site(kind: str) -> None:
    # docs/howto.rst merges config in reverse of this order so the user directory wins.
    dirs = platformdirs.PlatformDirs("MyApp", "MyCompany", version="1.0")
    assert next(getattr(dirs, f"iter_{kind}_dirs")()) == getattr(dirs, f"user_{kind}_dir")


def _result(path: Path, status: DirectoryStatus, error: OSError | None = None) -> DirectoryCreationResult:
    return DirectoryCreationResult(path=path, status=status, error=error)


def test_ensure_directories_exist_creates_new_dirs_with_parents(tmp_path: Path) -> None:
    first = tmp_path / "a"
    second = tmp_path / "nested" / "b"
    results = platformdirs.PlatformDirs().ensure_directories_exist([first, second])

    assert results == [_result(first, DirectoryStatus.CREATED), _result(second, DirectoryStatus.CREATED)]
    assert first.is_dir()
    assert second.is_dir()
    assert (tmp_path / "nested").is_dir()
    assert all(result.error is None for result in results)


def test_ensure_directories_exist_reports_preexisting_dirs(tmp_path: Path) -> None:
    first = tmp_path / "a"
    second = tmp_path / "b"
    first.mkdir()
    second.mkdir()

    results = platformdirs.PlatformDirs().ensure_directories_exist([str(first), second])

    assert results == [_result(first, DirectoryStatus.EXISTED), _result(second, DirectoryStatus.EXISTED)]
    assert all(result.error is None for result in results)


def test_ensure_directories_exist_preserves_order_and_accepts_strings(tmp_path: Path) -> None:
    existing = tmp_path / "existing"
    created = tmp_path / "created"
    existing.mkdir()

    results = platformdirs.PlatformDirs().ensure_directories_exist([str(created), str(existing)])

    assert [result.path for result in results] == [created, existing]
    assert [result.status for result in results] == [DirectoryStatus.CREATED, DirectoryStatus.EXISTED]


def test_ensure_directories_exist_deduplicates_paths(tmp_path: Path) -> None:
    target = tmp_path / "a"

    results = platformdirs.PlatformDirs().ensure_directories_exist([target, target, str(target)])

    assert results == [_result(target, DirectoryStatus.CREATED)]


def test_ensure_directories_exist_accepts_empty_batch() -> None:
    assert platformdirs.PlatformDirs().ensure_directories_exist(()) == []


def test_ensure_directories_exist_reports_file_conflict(tmp_path: Path) -> None:
    conflict = tmp_path / "a"
    conflict.write_text("")
    unaffected = tmp_path / "b"

    results = platformdirs.PlatformDirs().ensure_directories_exist([conflict, unaffected])

    assert len(results) == 2
    assert results[0].status is DirectoryStatus.FAILED
    assert isinstance(results[0].error, FileExistsError)
    assert results[0].error is not None
    assert results[0].error.errno == errno.EEXIST
    assert results[1] == _result(unaffected, DirectoryStatus.CREATED)
    assert conflict.is_file()  # the conflicting file is untouched


def test_ensure_directories_exist_reports_file_conflict_in_parent(tmp_path: Path) -> None:
    blocker = tmp_path / "blocker"
    blocker.write_text("")
    target = blocker / "nested"

    results = platformdirs.PlatformDirs().ensure_directories_exist([target])

    assert len(results) == 1
    assert results[0].path == target
    assert results[0].status is DirectoryStatus.FAILED
    assert isinstance(results[0].error, OSError)
    assert not target.exists()


@pytest.mark.skipif(sys.platform == "win32", reason="the read-only permission bit does not block creation on Windows")
def test_ensure_directories_exist_reports_permission_error(tmp_path: Path) -> None:
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("root bypasses directory permission checks")
    readonly = tmp_path / "readonly"
    readonly.mkdir()
    readonly.chmod(0o555)
    target = readonly / "nested"

    try:
        results = platformdirs.PlatformDirs().ensure_directories_exist([target])
    finally:
        readonly.chmod(0o755)

    assert results[0].status is DirectoryStatus.FAILED
    assert isinstance(results[0].error, PermissionError)
    assert not target.exists()


def test_ensure_directories_exist_continues_after_failure_without_rollback(tmp_path: Path) -> None:
    first = tmp_path / "a"
    conflict = tmp_path / "blocker"
    conflict.write_text("")
    third = tmp_path / "c"

    results = platformdirs.PlatformDirs().ensure_directories_exist([first, conflict, third])

    assert [result.status for result in results] == [
        DirectoryStatus.CREATED,
        DirectoryStatus.FAILED,
        DirectoryStatus.CREATED,
    ]
    assert first.is_dir()
    assert third.is_dir()


def test_ensure_directories_exist_rollback_removes_only_created_dirs(tmp_path: Path) -> None:
    created_first = tmp_path / "a"
    preexisting = tmp_path / "existing"
    preexisting.mkdir()
    marker = preexisting / "keep-me"
    marker.write_text("")
    created_second = tmp_path / "b"
    conflict = tmp_path / "blocker"
    conflict.write_text("")

    results = platformdirs.PlatformDirs().ensure_directories_exist(
        [created_first, preexisting, created_second, conflict],
        rollback=True,
    )

    by_path = {result.path: result for result in results}
    assert by_path[created_first].status is DirectoryStatus.ROLLED_BACK
    assert by_path[preexisting].status is DirectoryStatus.EXISTED
    assert by_path[created_second].status is DirectoryStatus.ROLLED_BACK
    assert by_path[conflict].status is DirectoryStatus.FAILED
    assert not created_first.exists()
    assert not created_second.exists()
    assert preexisting.is_dir()  # pre-existing directories must survive rollback...
    assert marker.is_file()  # ...along with everything they contain


def test_ensure_directories_exist_rollback_removes_created_parent_chain(tmp_path: Path) -> None:
    preexisting_base = tmp_path / "base"
    preexisting_base.mkdir()
    marker = preexisting_base / "keep-me"
    marker.write_text("")
    under_existing = preexisting_base / "new" / "nested"
    brand_new_base = tmp_path / "root" / "x" / "y"
    conflict = tmp_path / "blocker"
    conflict.write_text("")

    results = platformdirs.PlatformDirs().ensure_directories_exist(
        [under_existing, brand_new_base, conflict],
        rollback=True,
    )

    by_path = {result.path: result for result in results}
    assert by_path[under_existing].status is DirectoryStatus.ROLLED_BACK
    assert by_path[brand_new_base].status is DirectoryStatus.ROLLED_BACK
    assert by_path[conflict].status is DirectoryStatus.FAILED
    assert not (preexisting_base / "new").exists()
    assert preexisting_base.is_dir()
    assert marker.is_file()
    assert not (tmp_path / "root").exists()


def test_ensure_directories_exist_rollback_without_failure_keeps_dirs(tmp_path: Path) -> None:
    first = tmp_path / "a"
    second = tmp_path / "b"

    results = platformdirs.PlatformDirs().ensure_directories_exist([first, second], rollback=True)

    assert [result.status for result in results] == [DirectoryStatus.CREATED, DirectoryStatus.CREATED]
    assert first.is_dir()
    assert second.is_dir()


def test_ensure_directories_exist_rollback_leaves_nonempty_created_dir(tmp_path: Path, mocker: MockerFixture) -> None:
    first = tmp_path / "a"
    second = tmp_path / "b"
    conflict = tmp_path / "blocker"
    conflict.write_text("")
    real_rmdir = Path.rmdir

    def fake_rmdir(self: Path) -> None:
        if self == first:  # Simulate another process filling the directory before rollback.
            raise OSError(errno.ENOTEMPTY, "simulated")
        real_rmdir(self)

    mocker.patch.object(Path, "rmdir", new=fake_rmdir)

    results = platformdirs.PlatformDirs().ensure_directories_exist([first, second, conflict], rollback=True)

    by_path = {result.path: result for result in results}
    assert by_path[first].status is DirectoryStatus.CREATED  # best effort: non-empty directory is left behind
    assert by_path[second].status is DirectoryStatus.ROLLED_BACK
    assert by_path[conflict].status is DirectoryStatus.FAILED
    assert first.is_dir()
    assert not second.exists()


def test_ensure_directories_exist_rollback_undoes_parents_created_before_failure(
    tmp_path: Path, mocker: MockerFixture
) -> None:
    new_parent = tmp_path / "new-parent"
    target = new_parent / "leaf"
    real_mkdir = Path.mkdir

    def fake_mkdir(self: Path, mode: int = 0o777, parents: bool = False, exist_ok: bool = False) -> None:
        if self == target:  # Simulate a file appearing at the leaf while we create the parents.
            raise FileExistsError(errno.EEXIST, "simulated")
        real_mkdir(self, mode, parents, exist_ok)

    mocker.patch.object(Path, "mkdir", new=fake_mkdir)
    mocker.patch.object(Path, "is_dir", return_value=False)

    results = platformdirs.PlatformDirs().ensure_directories_exist([target], rollback=True)

    assert results[0].status is DirectoryStatus.FAILED
    assert isinstance(results[0].error, FileExistsError)
    assert not new_parent.exists()  # the parent created just before the failure is rolled back too


def test_ensure_directories_exist_handles_concurrent_creator_directory(tmp_path: Path, mocker: MockerFixture) -> None:
    target = tmp_path / "a"
    real_exists = Path.exists

    def fake_exists(self: Path) -> bool:
        if self == target:
            return False  # we observe the leaf as missing, then lose the creation race
        return real_exists(self)

    mocker.patch.object(Path, "exists", new=fake_exists)
    mocker.patch.object(Path, "mkdir", side_effect=FileExistsError(errno.EEXIST, "simulated"))
    mocker.patch.object(Path, "is_dir", return_value=True)  # the winner created a directory

    results = platformdirs.PlatformDirs().ensure_directories_exist([target])

    assert results == [_result(target, DirectoryStatus.EXISTED)]


def test_ensure_directories_exist_handles_concurrent_creator_file(tmp_path: Path, mocker: MockerFixture) -> None:
    target = tmp_path / "a"
    real_exists = Path.exists

    def fake_exists(self: Path) -> bool:
        if self == target:
            return False  # we observe the leaf as missing, then a file appears there
        return real_exists(self)

    mocker.patch.object(Path, "exists", new=fake_exists)
    mocker.patch.object(Path, "mkdir", side_effect=FileExistsError(errno.EEXIST, "simulated"))
    mocker.patch.object(Path, "is_dir", return_value=False)  # the winner created a file

    results = platformdirs.PlatformDirs().ensure_directories_exist([target])

    assert results[0].status is DirectoryStatus.FAILED
    assert isinstance(results[0].error, FileExistsError)


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX style filesystem root used in the scan")
def test_ensure_directories_exist_when_no_ancestor_exists(mocker: MockerFixture) -> None:
    mocker.patch.object(Path, "exists", return_value=False)

    results = platformdirs.PlatformDirs().ensure_directories_exist([Path("/this-root-does-not-exist/sub")])

    assert results[0].status is DirectoryStatus.FAILED
    assert isinstance(results[0].error, OSError)


def test_ensure_directories_exist_is_safe_across_threads(tmp_path: Path) -> None:
    targets = [tmp_path / name for name in ("a", "b", "c")]
    dirs = platformdirs.PlatformDirs()
    outcomes: list[DirectoryCreationResult] = []
    outcomes_lock = threading.Lock()
    worker_count = 8
    barrier = threading.Barrier(worker_count)

    def worker() -> None:
        barrier.wait()
        results = dirs.ensure_directories_exist(targets)
        with outcomes_lock:
            outcomes.extend(results)

    threads = [threading.Thread(target=worker) for _ in range(worker_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    for target in targets:
        matching = [result for result in outcomes if result.path == target]
        assert len(matching) == worker_count
        assert sum(result.status is DirectoryStatus.CREATED for result in matching) == 1
        assert all(result.status in {DirectoryStatus.CREATED, DirectoryStatus.EXISTED} for result in matching)
        assert target.is_dir()


def test_ensure_directories_exist_module_function(tmp_path: Path) -> None:
    target = tmp_path / "a"

    results = platformdirs.ensure_directories_exist([target])

    assert results == [_result(target, DirectoryStatus.CREATED)]
    assert target.is_dir()
