#  SPDX-FileCopyrightText: 2024-2026 Damon Lynch <damonlynch@gmail.com>
#  SPDX-License-Identifier: GPL-3.0-or-later

import sys
from pathlib import Path

from hatch_argparse_manpage.plugin import ArgparseManpageBuildHook


def test_build_command_line_options(make_hook) -> None:
    hook = make_hook(
        {
            "manpages": [
                "man/foo.1:object=parser:pyfile=bin/foo.py:format=pretty:"
                "author=Damon Lynch <dl@example.com>:description=The foo tool"
            ]
        },
        project_config={"name": "foo", "urls": {"Homepage": "https://example.com"}},
    )
    hook.load_argparse_manpage_config(full_spec=True)
    args = hook._build_command_line_options(hook._manpages_to_build[0])

    assert args.startswith(f"--output {Path('man') / 'foo.1'}")
    assert "--object parser" in args
    assert "--pyfile bin/foo.py" in args
    assert "--format pretty" in args
    assert '--author "Damon Lynch" --author-email "<dl@example.com>"' in args
    assert '--description "The foo tool"' in args
    assert '--project-name "foo"' in args
    assert '--url "https://example.com"' in args
    assert "  " not in args  # extraneous whitespace removed


def test_build_command_line_options_module_import(make_hook) -> None:
    hook = make_hook({"manpages": ["man/bar.8:module=mypkg.cli"]})
    hook.load_argparse_manpage_config(full_spec=True)
    args = hook._build_command_line_options(hook._manpages_to_build[0])

    assert "--module mypkg.cli" in args
    assert "--format" not in args
    assert "--author" not in args


def test_build_command_line_options_multiple_authors(make_hook) -> None:
    hook = make_hook(
        {"manpages": ["man/a.1:function=f:author=A B <ab@x.y>:author=C D <cd@x.y>"]}
    )
    hook.load_argparse_manpage_config(full_spec=True)
    args = hook._build_command_line_options(hook._manpages_to_build[0])

    assert '--author "A B" --author-email "<ab@x.y>"' in args
    assert '--author "C D" --author-email "<cd@x.y>"' in args


def test_assemble_command_windows_passthrough(monkeypatch) -> None:
    monkeypatch.setattr(sys, "platform", "win32")
    cmd = ArgparseManpageBuildHook._assemble_command("argparse-manpage --output x y")
    assert cmd == "argparse-manpage --output x y"


def test_assemble_command_posix_split(monkeypatch) -> None:
    monkeypatch.setattr(sys, "platform", "linux")
    cmd = ArgparseManpageBuildHook._assemble_command("argparse-manpage --output 'a b'")
    assert cmd == ["argparse-manpage", "--output", "a b"]
