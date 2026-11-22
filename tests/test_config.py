#  SPDX-FileCopyrightText: 2024-2026 Damon Lynch <damonlynch@gmail.com>
#  SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

import pytest

from hatch_argparse_manpage.plugin import ArgparseManpageBuildHook

AUTHOR_PAIR = ArgparseManpageBuildHook.AUTHOR_PAIR


def test_basic_parsing(make_hook) -> None:
    hook = make_hook(
        {
            "manpages": [
                "man/foo.1:object=parser:pyfile=bin/foo.py:format=pretty:"
                "author=Damon Lynch <dl@example.com>:description=The foo tool"
            ]
        },
        project_config={
            "name": "foo",
            "authors": [{"name": "Fallback", "email": "fb@example.com"}],
            "urls": {"Homepage": "https://example.com/home", "Issues": "https://x/i"},
        },
    )
    hook.load_argparse_manpage_config(full_spec=True)

    entry = hook._manpages_to_build[0]
    assert entry.manpage == "foo.1"
    assert entry.manpage_dir == Path("man")

    options = entry.options
    assert options["object_type"] == "object"
    assert options["object_name"] == "parser"
    assert options["import_type"] == "pyfile"
    assert options["import_from"] == "bin/foo.py"
    assert options["format"] == "pretty"
    assert options["description"] == "The foo tool"
    # Configured authors take precedence over the project metadata ones
    assert options[AUTHOR_PAIR] == [("Damon Lynch", "dl@example.com")]
    assert options["project_name"] == "foo"
    assert options["version"] == "1.2.3"
    assert options["url"] == "https://example.com/home"
    assert options["prog"] == "foo.py"


@pytest.mark.parametrize(
    ("spec", "fragment"),
    [
        ("man/a.1:function=f:object=g", "object type"),
        ("man/a.1:pyfile=f:module=g", "import type"),
        ("man/a.1:format=pretty:format=single-commands-section", "format"),
        ("man/a.1:description=x:description=y", "the option"),
    ],
)
def test_duplicate_options_rejected(make_hook, spec: str, fragment: str) -> None:
    hook = make_hook({"manpages": [spec]})
    with pytest.raises(ValueError, match="already configured") as exc_info:
        hook.load_argparse_manpage_config(full_spec=True)
    assert fragment in str(exc_info.value)
    # The message must not repeat "is already configured" twice
    assert str(exc_info.value).count("is already configured") == 1


def test_unknown_options_ignored(make_hook) -> None:
    hook = make_hook({"manpages": ["man/a.1:function=f:not_a_valid_option=x"]})
    hook.load_argparse_manpage_config(full_spec=True)
    assert "not_a_valid_option" not in hook._manpages_to_build[0].options


def test_missing_manpages_config(make_hook) -> None:
    hook = make_hook({})
    with pytest.raises(ValueError, match="Configure"):
        hook.load_argparse_manpage_config(full_spec=False)


def test_manpages_not_a_list(make_hook) -> None:
    hook = make_hook({"manpages": "man/a.1:function=f"})
    with pytest.raises(TypeError, match="list"):
        hook.load_argparse_manpage_config(full_spec=False)


def test_manpage_dir_must_be_within_root(make_hook) -> None:
    # A man page directly in the project root is rejected
    hook = make_hook({"manpages": ["a.1:function=f"]}, root=".")
    with pytest.raises(ValueError, match="within"):
        hook.load_argparse_manpage_config(full_spec=False)


def test_clean_mode_defers_full_spec(make_hook) -> None:
    hook = make_hook({"manpages": ["man/a.1:function=parser"]})
    hook.load_argparse_manpage_config(full_spec=False)
    assert hook._manpages_to_build[0].options == {}
    assert list(hook.manpages_to_build) == [str(Path("man") / "a.1")]


def test_authors_fallback_from_project(make_hook) -> None:
    hook = make_hook(
        {"manpages": ["man/a.1:function=f"]},
        project_config={
            "authors": [
                {"name": "A B", "email": "ab@example.com"},
                {"name": "", "email": ""},
            ]
        },
    )
    hook.load_argparse_manpage_config(full_spec=True)
    options = hook._manpages_to_build[0].options
    assert options[AUTHOR_PAIR] == [("A B", "ab@example.com")]


def test_multiple_authors_accumulate(make_hook) -> None:
    hook = make_hook(
        {"manpages": ["man/a.1:function=f:author=A B <ab@x.y>:author=C D <cd@x.y>"]}
    )
    hook.load_argparse_manpage_config(full_spec=True)
    options = hook._manpages_to_build[0].options
    assert options[AUTHOR_PAIR] == [("A B", "ab@x.y"), ("C D", "cd@x.y")]


def test_no_authors_configured_at_all(make_hook) -> None:
    hook = make_hook({"manpages": ["man/a.1:function=f"]}, project_config={})
    hook.load_argparse_manpage_config(full_spec=True)
    assert AUTHOR_PAIR not in hook._manpages_to_build[0].options


def test_url_single_entry_used(make_hook) -> None:
    hook = make_hook(
        {"manpages": ["man/a.1:function=f"]},
        project_config={"urls": {"Download": "https://only.one"}},
    )
    hook.load_argparse_manpage_config(full_spec=True)
    assert hook._manpages_to_build[0].options["url"] == "https://only.one"


def test_url_homepage_preferred_case_insensitively(make_hook) -> None:
    hook = make_hook(
        {"manpages": ["man/a.1:function=f"]},
        project_config={"urls": {"home-page": "https://hp", "Docs": "https://d"}},
    )
    hook.load_argparse_manpage_config(full_spec=True)
    assert hook._manpages_to_build[0].options["url"] == "https://hp"


def test_url_omitted_when_ambiguous(make_hook) -> None:
    hook = make_hook(
        {"manpages": ["man/a.1:function=f"]},
        project_config={"urls": {"Docs": "https://d", "Download": "https://dl"}},
    )
    hook.load_argparse_manpage_config(full_spec=True)
    assert "url" not in hook._manpages_to_build[0].options


def test_explicit_options_override_project_metadata(make_hook) -> None:
    hook = make_hook(
        {"manpages": ["man/a.1:function=f:version=9.9:project_name=bar:prog=baz"]},
        project_config={"name": "foo"},
        version="1.2.3",
    )
    hook.load_argparse_manpage_config(full_spec=True)
    options = hook._manpages_to_build[0].options
    assert options["version"] == "9.9"
    assert options["project_name"] == "bar"
    assert options["prog"] == "baz"


def test_prog_defaults_to_empty_without_pyfile(make_hook) -> None:
    hook = make_hook({"manpages": ["man/a.1:module=mypkg.cli"]})
    hook.load_argparse_manpage_config(full_spec=True)
    assert hook._manpages_to_build[0].options["prog"] == ""


def test_include_url_false_removes_url(make_hook) -> None:
    hook = make_hook(
        {
            "manpages": ["man/a.1:function=f"],
            "include-url": False,
            "force-command-line": True,
        },
        project_config={"urls": {"Homepage": "https://x"}},
    )
    hook.load_argparse_manpage_config(full_spec=True)
    assert hook._include_url is False
    assert hook._force_command_line is True

    entry = hook._manpages_to_build[0]
    assert entry.options["url"] == "https://x"
    hook.apply_config_options(entry)
    assert "url" not in entry.options


def test_include_url_default_keeps_url(make_hook) -> None:
    hook = make_hook(
        {"manpages": ["man/a.1:function=f"]},
        project_config={"urls": {"Homepage": "https://x"}},
    )
    hook.load_argparse_manpage_config(full_spec=True)
    assert hook._include_url is True
    entry = hook._manpages_to_build[0]
    hook.apply_config_options(entry)
    assert entry.options["url"] == "https://x"
