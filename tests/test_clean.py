#  SPDX-FileCopyrightText: 2024-2026 Damon Lynch <damonlynch@gmail.com>
#  SPDX-License-Identifier: GPL-3.0-or-later

import pytest


def _build_manpage(hook) -> None:
    hook.load_argparse_manpage_config(full_spec=True)
    entry = hook._manpages_to_build[0]
    hook.apply_config_options(entry)
    hook._build_manpage(entry)


def test_clean_round_trip(make_hook, demo_project) -> None:
    hook = make_hook({"manpages": ["man/foo.1:object=parser:pyfile=bin/foo.py"]})
    _build_manpage(hook)
    page = demo_project / "man" / "foo.1"
    assert page.exists()

    hook.clean(["sdist"])

    assert not page.exists()
    assert not (demo_project / "man").exists()
    assert (demo_project / "bin" / "foo.py").exists()


def test_clean_keeps_directory_with_foreign_files(make_hook, demo_project) -> None:
    hook = make_hook({"manpages": ["man/foo.1:object=parser:pyfile=bin/foo.py"]})
    _build_manpage(hook)
    keeper = demo_project / "man" / "keep.txt"
    keeper.write_text("mine", encoding="utf-8")

    hook.clean([])

    assert not (demo_project / "man" / "foo.1").exists()
    assert (demo_project / "man").exists()
    assert keeper.read_text(encoding="utf-8") == "mine"


def test_clean_removes_tree_of_empty_subdirectories(make_hook, demo_project) -> None:
    hook = make_hook({"manpages": ["man/sub/foo.1:object=parser:pyfile=bin/foo.py"]})
    (demo_project / "man" / "sub").mkdir(parents=True)
    _build_manpage(hook)
    assert (demo_project / "man" / "sub" / "foo.1").exists()

    hook.clean([])

    assert not (demo_project / "man" / "sub").exists()
    # Only the man page's own directory tree is pruned, not its parents
    assert (demo_project / "man").exists()


def test_clean_preserves_tree_with_file_in_subdirectory(
    make_hook, demo_project
) -> None:
    hook = make_hook({"manpages": ["man/sub/foo.1:object=parser:pyfile=bin/foo.py"]})
    (demo_project / "man" / "sub").mkdir(parents=True)
    _build_manpage(hook)
    keeper = demo_project / "man" / "sub" / "keep.txt"
    keeper.write_text("mine", encoding="utf-8")

    hook.clean([])

    assert not (demo_project / "man" / "sub" / "foo.1").exists()
    assert (demo_project / "man" / "sub").exists()
    assert keeper.read_text(encoding="utf-8") == "mine"


def test_has_only_subdirectories(make_hook, tmp_path) -> None:
    hook = make_hook({})
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)
    assert hook._has_only_subdirectories(tmp_path / "a")

    (deep / "f.txt").write_text("x", encoding="utf-8")
    assert not hook._has_only_subdirectories(tmp_path / "a")


def test_clean_files_ignores_missing(make_hook, tmp_path) -> None:
    hook = make_hook({})
    hook._clean_files(["man/nothing.1"])
    assert not (tmp_path / "man").exists()


def test_clean_requires_manpages_config(make_hook) -> None:
    hook = make_hook({})
    with pytest.raises(ValueError, match="Configure"):
        hook.clean([])
