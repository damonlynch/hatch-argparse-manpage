#  SPDX-FileCopyrightText: 2024-2026 Damon Lynch <damonlynch@gmail.com>
#  SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from hatch_argparse_manpage.plugin import ArgparseManpageBuildHook


@pytest.fixture
def make_hook(tmp_path: Path) -> Callable[..., ArgparseManpageBuildHook]:
    """
    Build a real hook instance with its injected dependencies stubbed.

    The constructor arguments mirror what Hatch passes during a build, so
    the hook's own properties (root, config, metadata, target_name, app)
    work exactly as in production.
    """

    def factory(
        config: dict[str, Any] | None = None,
        project_config: dict[str, Any] | None = None,
        version: str = "1.2.3",
        root: Path | str | None = None,
        target_name: str = "sdist",
    ) -> ArgparseManpageBuildHook:
        hook = ArgparseManpageBuildHook(
            root=str(tmp_path if root is None else root),
            config=config if config is not None else {},
            build_config=None,
            metadata=SimpleNamespace(
                config={} if project_config is None else {"project": project_config},
                version=version,
            ),
            directory="",
            target_name=target_name,
            app=SimpleNamespace(verbosity=-10),
        )
        # Production only ever runs through initialize()/clean(), which set
        # this up first, so do the same here for direct-path tests
        hook.setup_console()
        return hook

    return factory


@pytest.fixture
def demo_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    A minimal project layout with an importable CLI, used for end-to-end
    man page generation. The working directory is switched to it because
    argparse-manpage resolves pyfile paths relative to the cwd.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "foo.py").write_text(
        "import argparse\n"
        "\n"
        "parser = argparse.ArgumentParser(prog='foo', description='Demo foo')\n"
        'parser.add_argument("--verbose", action="store_true", help="Verbose")\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    return tmp_path
