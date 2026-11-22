#  SPDX-FileCopyrightText: 2024-2026 Damon Lynch <damonlynch@gmail.com>
#  SPDX-License-Identifier: GPL-3.0-or-later

import shlex
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from hatch_argparse_manpage.plugin import ManpageGenerationError


def test_direct_build_creates_manpage(make_hook, demo_project) -> None:
    hook = make_hook(
        {
            "manpages": [
                "man/foo.1:object=parser:pyfile=bin/foo.py:"
                "author=Damon Lynch <dl@example.com>"
            ]
        },
        project_config={"name": "foo", "urls": {"Homepage": "https://example.com"}},
    )
    hook.load_argparse_manpage_config(full_spec=True)
    entry = hook._manpages_to_build[0]
    hook.apply_config_options(entry)
    hook._build_manpage(entry)

    page = demo_project / "man" / "foo.1"
    assert page.exists()
    content = page.read_text(encoding="utf-8")
    assert ".TH" in content
    assert "verbose" in content.lower()


def test_direct_build_rejects_invalid_format(make_hook, demo_project) -> None:
    hook = make_hook({"manpages": ["man/foo.1:object=parser:pyfile=bin/foo.py"]})
    hook.load_argparse_manpage_config(full_spec=True)
    entry = hook._manpages_to_build[0]
    entry.options["format"] = "weird"
    with pytest.raises(ValueError, match="Invalid format"):
        hook._build_manpage(entry)
    assert not (demo_project / "man").exists()  # nothing was written


def test_do_work_end_to_end(make_hook, demo_project) -> None:
    hook = make_hook({"manpages": ["man/foo.1:object=parser:pyfile=bin/foo.py"]})
    build_data = {"artifacts": []}
    hook.do_work(build_data)

    assert build_data["artifacts"] == [str(Path("man") / "foo.1")]
    assert (demo_project / "man" / "foo.1").exists()


def test_cmdline_failure_raises(make_hook, monkeypatch) -> None:
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["kwargs"] = kwargs
        return SimpleNamespace(returncode=1, stderr="bad thing", stdout="partial")

    monkeypatch.setattr(subprocess, "run", fake_run)
    hook = make_hook({})
    with pytest.raises(ManpageGenerationError, match="argparse-manpage") as exc_info:
        hook._create_man_page_using_cmdline("--output x")
    assert "bad thing" in str(exc_info.value)
    assert captured["kwargs"]["check"] is False
    assert captured["kwargs"]["capture_output"] is True


def test_cmdline_success_does_not_raise(make_hook, monkeypatch) -> None:
    captured = {}

    def fake_run(cmd, **_kwargs):
        captured["cmd"] = cmd
        return SimpleNamespace(returncode=0, stderr="", stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    hook = make_hook({})
    hook._create_man_page_using_cmdline("--output x")
    # _assemble_command passes a string on Windows and an argv list elsewhere,
    # so compare the resolved arguments rather than the container type; both
    # shapes are pinned for themselves in test_command_line_options.py
    cmd = captured["cmd"]
    argv = shlex.split(cmd) if isinstance(cmd, str) else cmd
    assert argv == ["argparse-manpage", "--output", "x"]


def test_build_manpages_falls_back_to_cmdline(make_hook, monkeypatch) -> None:
    hook = make_hook({"manpages": ["man/a.1:module=pkg.cli"]})
    hook.load_argparse_manpage_config(full_spec=True)

    def boom(_build_options) -> None:
        msg = "internal API broke"
        raise RuntimeError(msg)

    retried = []
    monkeypatch.setattr(hook, "_build_manpage", boom)
    monkeypatch.setattr(hook, "_build_using_cmdline", retried.append)
    hook.build_manpages()
    assert len(retried) == 1


def test_build_manpages_direct_success_skips_cmdline(make_hook, monkeypatch) -> None:
    hook = make_hook({"manpages": ["man/a.1:module=pkg.cli"]})
    hook.load_argparse_manpage_config(full_spec=True)

    direct = []
    monkeypatch.setattr(hook, "_build_manpage", direct.append)

    def no_cmdline(_build_options) -> None:
        msg = "command line must not be used"
        raise AssertionError(msg)

    monkeypatch.setattr(hook, "_build_using_cmdline", no_cmdline)
    hook.build_manpages()
    assert len(direct) == 1


def test_force_command_line_skips_direct_api(make_hook, monkeypatch) -> None:
    hook = make_hook(
        {"manpages": ["man/a.1:module=pkg.cli"], "force-command-line": True}
    )
    hook.load_argparse_manpage_config(full_spec=True)

    def no_direct(_build_options) -> None:
        msg = "direct API must not be used"
        raise AssertionError(msg)

    retried = []
    monkeypatch.setattr(hook, "_build_manpage", no_direct)
    monkeypatch.setattr(hook, "_build_using_cmdline", retried.append)
    hook.build_manpages()
    assert len(retried) == 1
