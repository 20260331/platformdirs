"""Read-only command line interface for querying platform directories.

Run ``python -m platformdirs --help`` for usage. The CLI only computes paths: it never creates directories and never
modifies the process environment (``ensure_exists`` is always disabled and cannot be enabled).

Exit codes:

* ``0`` - success
* ``2`` - invalid command line arguments (the standard ``argparse`` usage error code)
* ``3`` - the requested directory category is not supported on the current platform

"""

from __future__ import annotations

import argparse
import json
import sys
from typing import TYPE_CHECKING

from platformdirs import PlatformDirs

if TYPE_CHECKING:
    from collections.abc import Sequence

PROPS = (
    "user_data_dir",
    "user_config_dir",
    "user_cache_dir",
    "user_state_dir",
    "user_log_dir",
    "user_documents_dir",
    "user_downloads_dir",
    "user_pictures_dir",
    "user_videos_dir",
    "user_music_dir",
    "user_desktop_dir",
    "user_projects_dir",
    "user_publicshare_dir",
    "user_templates_dir",
    "user_fonts_dir",
    "user_preference_dir",
    "user_bin_dir",
    "site_bin_dir",
    "user_applications_dir",
    "user_runtime_dir",
    "site_data_dir",
    "site_config_dir",
    "site_cache_dir",
    "site_state_dir",
    "site_log_dir",
    "site_applications_dir",
    "site_runtime_dir",
)

#: Exit code used when a directory category is not supported on the current platform.
EXIT_UNSUPPORTED = 3


class UnsupportedCategoryError(RuntimeError):
    """A directory category cannot be resolved on the current platform."""


def _build_parser() -> argparse.ArgumentParser:
    """Build the command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="platformdirs",
        description="Query platform-specific directories without creating them or modifying the environment.",
    )
    parser.add_argument(
        "category",
        nargs="?",
        choices=PROPS,
        metavar="category",
        help="directory category to query (default: print the complete set of directories)",
    )
    parser.add_argument("-a", "--appname", help="application name used to build application-specific paths")
    author_group = parser.add_mutually_exclusive_group()
    author_group.add_argument(
        "--appauthor",
        help="application author used to build application-specific paths (defaults to the application name)",
    )
    author_group.add_argument(
        "--no-appauthor",
        dest="appauthor",
        action="store_const",
        const=False,
        help="omit the application author component when building paths",
    )
    parser.add_argument("--version", dest="version", help="application version appended to application-specific paths")
    parser.add_argument(
        "-f",
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format: 'text' for humans or 'json' for stable machine-readable output (default: text)",
    )
    return parser


def _read_category(dirs: PlatformDirs, category: str) -> str:
    """Resolve a single directory category, translating platform failures to `UnsupportedCategoryError`."""
    try:
        return getattr(dirs, category)
    except NotImplementedError as exc:
        msg = f"directory category {category!r} is not supported on this platform ({sys.platform!r})"
        raise UnsupportedCategoryError(msg) from exc


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line interface and return the process exit code."""
    args = _build_parser().parse_args(argv)

    # ``ensure_exists`` is hard-wired off so the query can never create directories.
    dirs = PlatformDirs(
        appname=args.appname,
        appauthor=args.appauthor,
        version=args.version,
        ensure_exists=False,
    )
    categories = PROPS if args.category is None else (args.category,)

    result: dict[str, str] = {}
    try:
        for category in categories:
            result[category] = _read_category(dirs, category)
    except UnsupportedCategoryError as exc:
        sys.stderr.write(f"platformdirs: error: {exc}\n")
        return EXIT_UNSUPPORTED

    if args.format == "json":
        # Insertion order follows ``categories`` (the fixed ``PROPS`` order for the complete set), keeping output stable.
        sys.stdout.write(f"{json.dumps(result, indent=2)}\n")
    elif args.category is None:
        sys.stdout.write("".join(f"{name}: {path}\n" for name, path in result.items()))
    else:
        sys.stdout.write(f"{result[args.category]}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
