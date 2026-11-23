#  SPDX-FileCopyrightText: 2024-2026 Damon Lynch <damonlynch@gmail.com>
#  SPDX-License-Identifier: GPL-3.0-or-later

import sys
from pathlib import Path


def test_initialize_skips_unknown_target(make_hook, monkeypatch) -> None:
    hook = make_hook({"manpages": ["man/a.1:function=f"]}, target_name="custom-target")
    calls = []
    monkeypatch.setattr(hook, "do_work", calls.append)
    hook.initialize("1.2.3", {"artifacts": []})
    assert calls == []


def test_initialize_skips_configured_platform(make_hook, monkeypatch) -> None:
    monkeypatch.setattr(sys, "platform", "plan9")
    hook = make_hook(
        {"manpages": ["man/a.1:function=f"], "skip-platforms": ["plan9"]},
        target_name="wheel",
    )
    calls = []
    monkeypatch.setattr(hook, "do_work", calls.append)
    hook.initialize("1.2.3", {"artifacts": []})
    assert calls == []


def test_initialize_runs_on_other_platforms(make_hook, monkeypatch) -> None:
    monkeypatch.setattr(sys, "platform", "plan9")
    hook = make_hook(
        {"manpages": ["man/a.1:function=f"], "skip-platforms": ["linux"]},
        target_name="wheel",
    )
    calls = []
    monkeypatch.setattr(hook, "do_work", calls.append)
    hook.initialize("1.2.3", {"artifacts": []})
    assert len(calls) == 1


def test_initialize_end_to_end(make_hook, demo_project) -> None:
    hook = make_hook(
        {"manpages": ["man/foo.1:object=parser:pyfile=bin/foo.py"]},
        target_name="sdist",
    )
    build_data = {"artifacts": []}
    hook.initialize("1.2.3", build_data)

    assert build_data["artifacts"] == [str(Path("man") / "foo.1")]
    assert (demo_project / "man" / "foo.1").exists()
