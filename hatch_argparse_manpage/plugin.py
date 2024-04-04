# SPDX-FileCopyrightText: Copyright 2024 Damon Lynch <damonlynch@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import re
from email.utils import parseaddr
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterator, NamedTuple

import argparse_manpage.tooling
import argparse_manpage.manpage
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from rich.console import Console

ManpageOptions = dict[str, str | list[tuple[str, str]] | list[str]]


class ManpageToBuildOptions(NamedTuple):
    manpage: str
    manpage_dir: Path
    options: ManpageOptions


ManpageOptionsCollection = list[ManpageToBuildOptions]


class ArgparseManpageBuildHook(BuildHookInterface):
    """
    Compile GNU gettext translation files from po-format into
    mo-format using the GNU gettext utility msgfmt, and optionally translate files
    using the GNU gettext utility intltool-merge.

    Cleans up any files that it creates, and any resulting directories, but
    only if the directories are empty.
    """

    PLUGIN_NAME = "argparse-manpage"

    MANPAGE_OPTIONS = (
        "authors",
        "description",
        "long_description",
        "project_name",
        "prog",
        "url",
        "version",
        "format",
        "manual_section",
        "manual_title",
        "include",
        "manfile",
    )

    AUTHOR_PAIR = "authors_tuple"

    def config_name(self) -> str:
        return f"[tool.hatch.build.hooks.{self.PLUGIN_NAME}]"

    @staticmethod
    def _assemble_command(cmd: str) -> list[str] | str:
        if sys.platform == "win32":
            return cmd
        return shlex.split(cmd)

    def _create_man_page_using_cmdline(self, args: str) -> None:
        """
        Create a manual page using the utility argparse-manpage

        """

        cmd_str = f"argparse-manpage {args}"
        self.console_output(
            f"{cmd_str}", level=2, style=self._style_level_debug, highlight=False
        )
        cmd = self._assemble_command(cmd_str)
        process = subprocess.run(cmd, text=True, capture_output=True)
        if process.returncode:
            raise Exception(
                "Error while invoking argparse-manpage:\n"
                f"{process.stderr}\n{process.stdout}"
            )

    def _clean_files(self, relative_file_paths: Iterator[str]) -> None:
        project_root: Path = Path(self.root)
        for p in relative_file_paths:
            full_path = project_root / p
            if full_path.exists():
                self.console_output(
                    f"Removing {full_path}", level=2, style=self._style_level_debug
                )
                full_path.unlink()

    def _has_only_subdirectories(self, path: Path) -> bool:
        """
        Checks if a directory has only subdirectories and no files.

        :param path: the full path to the directory to check
        :return: True if the directory has only subdirectories and no files
        """

        for entry in path.iterdir():
            if entry.is_file():
                return False
            # Recursively check subdirectories
            if entry.is_dir() and not self._has_only_subdirectories(entry):
                return False
        return True

    def _clean_directory_tree_only_if_has_empty_subdirectories(
        self, folder: Path
    ) -> None:
        """
        Removes a directory tree only if it contains no files and any of its
        subdirectories in its tree likewise contain no files

        :param folder: full path of the directory
        """

        if folder.is_dir() and self._has_only_subdirectories(folder):
            self.console_output(
                f"Removing {folder}", level=2, style=self._style_level_debug
            )
            shutil.rmtree(folder)

    def clean(self, versions: list[str]) -> None:
        """
        Remove all files created by this plug-in, if they exist.

        Remove all their directories only they contain no other files,
        with the same being true of their subdirectories.

        :param versions: see Hatch documentation for details
        """

        self.setup_console()
        self.console_output(
            "Cleaning manual pages", level=1, style=self._style_level_waiting
        )

        self.load_argparse_manpage_config(full_spec=False)

        # Remove individual manpages, irrespective of folder
        self._clean_files(self.manpages_to_build)

        # Remove manpage build folders
        project_root: Path = Path(self.root)
        build_folders = (
            manpage.manpage_dir
            for manpage in self._manpages_to_build
            if manpage.manpage_dir != project_root
        )

        for folder in build_folders:
            self._clean_directory_tree_only_if_has_empty_subdirectories(folder)

        self.console_output(
            "Finished cleaning manual pages",
            level=1,
            style=self._style_level_success,
        )

    def _build_command_line_options(self, build_options: ManpageToBuildOptions) -> str:
        options = build_options.options
        manpage = f"--output {build_options.manpage_dir / build_options.manpage}"
        object = (
            f"--{options['object_type']} {options['object_name']}"
            if options.get("object_type") in ("function", "object")
            else ""
        )
        import_from = (
            f"--{options['import_type']} {options['import_from']}"
            if options.get("import_type") in ("pyfile", "module")
            else ""
        )
        format = f"--format {options['format']}" if "format" in options else ""

        # argparse-manpage expects pairs of --author --author-email
        authors = ""
        if self.AUTHOR_PAIR in options:
            authors = " ".join(
                f'--author "{author[0]}" --author-email "<{author[1]}>"'
                for author in options[self.AUTHOR_PAIR]
            )

        # Wrap command line values in double quotes
        other_options = " ".join(
            (
                f"--{key.replace('_', '-')} \"{options[key]}\""
                for key in self.MANPAGE_OPTIONS
                if key in options and key != self.AUTHOR_PAIR
            )
        )

        args = " ".join([manpage, object, import_from, format, authors, other_options])
        # Remove extraneous whitespace before returning string
        return re.sub(r"\s+", r" ", args)

    def _build_using_cmdline(self, build_options: ManpageToBuildOptions) -> None:
        cmd_str = self._build_command_line_options(build_options)
        self._create_man_page_using_cmdline(cmd_str)

    def _build_manpage(self, build_options: ManpageToBuildOptions) -> None:
        """
        Build manpage by directly calling argparse code, obviously using the data
        structures it expects. If those structures change, this code will break.
        """

        options = build_options.options
        page = str(build_options.manpage_dir / build_options.manpage)
        parser = argparse_manpage.tooling.get_parser(
            options["import_type"],
            options["import_from"],
            options["object_name"],
            options["object_type"],
            options.get("prog", None),
        )
        format = options.get("format", "pretty")
        assert format in ("pretty", "single-commands-section")

        # Convert tuple of author and author email into a string with email
        # surrounded by angle brackets
        if self.AUTHOR_PAIR in options:
            options["authors"] = [
                f"{author[0]} <{author[1]}>" for author in options[self.AUTHOR_PAIR]
            ]
            del options[self.AUTHOR_PAIR]

        manpage = argparse_manpage.manpage.Manpage(parser, format=format, _data=options)
        argparse_manpage.tooling.write_to_filename(str(manpage), page)

    def apply_config_options(self, build_options: ManpageToBuildOptions) -> None:
        """
        Applies any custom configuration options unique to this plugin that
        can be used to manipulate a manpage's appearance
        """

        if not self._include_url and "url" in build_options.options:
            del build_options.options["url"]

    def build_manpages(self) -> None:
        for build_options in self._manpages_to_build:
            self.console_output(
                f"Building manpage {build_options.manpage_dir / build_options.manpage}",
                level=2,
                style=self._style_level_info,
                highlight=False,
            )
            self.apply_config_options(build_options)

            if self._force_command_line:
                self._build_using_cmdline(build_options)
            else:
                try:
                    self._build_manpage(build_options)
                except Exception as e:
                    message = (
                        f"Exception: {e}\n"
                        f"Manpage {build_options.manpage_dir / build_options.manpage} "
                        "failed to build when directly calling argparse_manpage "
                        "Python code. Will retry using the command line program..."
                    )
                    self.console_output(
                        message=message,
                        level=0,
                        style=self._style_level_error,
                    )
                    self._build_using_cmdline(build_options)
                    self.console_output(
                        message="...generating using the command line succeeded",
                        level=0,
                        style=self._style_level_error,
                    )

    def _load_manpage_options(
        self, options: ManpageOptions, defn_components: list[str]
    ) -> None:
        self._project_config = self.metadata.config.get("project")
        basename = ""

        for defn in defn_components:
            option, value = defn.split("=")
            if option in ("function", "object"):
                try:
                    assert "object_type" not in options
                except AssertionError:
                    raise ValueError(
                        f"'{option}' is invalid: object type "
                        f"'{options['object_type']}' is already configured"
                    )
                options["object_type"] = option
                options["object_name"] = value

            elif option in ("pyfile", "module"):
                try:
                    assert "import_type" not in options
                except AssertionError:
                    raise ValueError(
                        f"'{option}' is invalid: import type "
                        f"'{options['import_type']}' is already configured"
                    )
                options["import_type"] = option
                options["import_from"] = value
                if option == "pyfile":
                    basename = Path(value).name

            elif option == "format":
                try:
                    assert "format" not in options
                except AssertionError:
                    raise ValueError(
                        f"'{option}' is invalid: format is already configured "
                        f"'{options['format']}' is already configured"
                    )
                options["format"] = value

            elif option == "author":
                if self.AUTHOR_PAIR not in options:
                    options[self.AUTHOR_PAIR] = []
                assert isinstance(options[self.AUTHOR_PAIR], list)
                options[self.AUTHOR_PAIR].append(extract_name_email(value))  # type: ignore

            elif option in self.MANPAGE_OPTIONS:
                try:
                    assert option not in options
                except AssertionError:
                    raise ValueError(
                        f"'{option}' is invalid: the option "
                        f"'{options[option]}' is already configured"
                    )
                options[option] = value

        if self._project_config is not None:
            if "url" not in options and "urls" in self._project_config:
                urls: dict[str, str] = self._project_config["urls"]
                url: str = ""
                # If there is only one URL, use it
                if len(urls) == 1:
                    url = list(urls.values())[0]
                else:
                    # If there is more than one URL, use the homepage
                    # Make dictionary keys lowercase
                    urls_lowercase = {k.lower(): v for k, v in urls.items()}
                    for key in ("homepage", "home-page"):
                        if key in urls_lowercase:
                            url = urls_lowercase[key]
                            break
                if url:
                    options["url"] = url

            if self.AUTHOR_PAIR not in options and "authors" in self._project_config:
                options[self.AUTHOR_PAIR] = []
                for author in self._project_config["authors"]:
                    name = author.get("name", "")
                    email = author.get("email", "")
                    if name or email:
                        options[self.AUTHOR_PAIR].append((name, email))  # type: ignore

            if "project_name" not in options and "name" in self._project_config:
                options["project_name"] = self._project_config["name"]

            if "version" not in options and self.metadata.version:
                options["version"] = self.metadata.version

        if "prog" not in options:
            options["prog"] = basename

    def load_argparse_manpage_config(self, full_spec: bool) -> None:
        """
        Load the argparse-manpage config from pyproject.toml using hatch's interface
        and assign the values to private class variables.

        :param full_spec: Whether to load the full specification from pyproject.toml.
         If running the clean operation, loading the full specification is unnecessary.
        """

        project_root: Path = Path(self.root)

        try:
            manpage_specs: list[str] = self.config["manpages"]
        except KeyError:
            raise ValueError(
                f'Configure "manpages" in "{self.config_name()}" in '
                "pyproject.toml to specify the manpages to generate"
            )
        try:
            assert isinstance(manpage_specs, list)
        except AssertionError:
            raise ValueError(
                f'Configure "manpages" in "{self.config_name()}" in '
                "pyproject.toml as a list of manpages to generate"
            )

        self._manpages_to_build: ManpageOptionsCollection = []
        self._include_url = True
        self._force_command_line = False

        for spec in manpage_specs:
            options: ManpageOptions = {}

            components = spec.strip().split(":")
            manpage_path = Path(components[0])

            manpage: str = manpage_path.name
            manpage_dir = manpage_path.parent

            if manpage_dir == project_root:
                raise ValueError(
                    "The directory storing the generated man page must be within the "
                    "project's base directory, and not equal to the project's base "
                    "directory"
                )

            if full_spec:
                self._load_manpage_options(
                    options=options, defn_components=components[1:]
                )
                self._include_url = self.config.get("include-url", True)
                self._force_command_line = self.config.get("force-command-line", False)

            self._manpages_to_build.append(
                ManpageToBuildOptions(
                    manpage=manpage, manpage_dir=manpage_dir, options=options
                )
            )

    @property
    def manpages_to_build(self) -> Iterator[str]:
        return (
            str(manpage.manpage_dir / manpage.manpage)
            for manpage in self._manpages_to_build
        )

    def do_work(self, build_data: dict[str, Any]) -> None:
        self.load_argparse_manpage_config(full_spec=True)
        build_data["artifacts"].extend(self.manpages_to_build)
        self.build_manpages()

    def setup_console(self) -> None:
        if self.app.verbosity < 0:
            return
        self.console = Console(force_terminal=True, force_interactive=False)

        # Match default Hatch color config:
        self._style_level_success = "bold cyan"
        self._style_level_error = "bold red"
        self._style_level_warning = "bold yellow"
        self._style_level_waiting = "bold magenta"
        self._style_level_info = "bold"
        self._style_level_debug = "bold"

    def console_output(
        self, message: str, level: int = 0, style: str = "", highlight=True
    ) -> None:
        if self.app.verbosity < level:
            return
        self.console.print(message, style=style, highlight=highlight)

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        if self.target_name not in ["wheel", "sdist"]:
            return

        self.setup_console()
        self.console_output(
            "Building manual pages", level=1, style=self._style_level_waiting
        )
        self.do_work(build_data)
        self.console_output(
            "Finished building manual pages",
            level=1,
            style=self._style_level_success,
        )


def extract_name_email(text: str) -> tuple[str, str]:
    """
    Parse a line of text to extract the name and/or email from it

    :param text: the line containing the name and/or email
    :return: a tuple containing the name and email

    >>> extract_name_email("Damon Lynch <damonlynch@gmail.com>")
    ('Damon Lynch', 'damonlynch@gmail.com')
    >>> extract_name_email("Damon Lynch damonlynch@gmail.com")
    ('Damon Lynch', 'damonlynch@gmail.com')
    >>> extract_name_email("Damon Lynch")
    ('Damon Lynch', '')
    >>> extract_name_email("damonlynch@gmail.com")
    ('', 'damonlynch@gmail.com')
    >>> extract_name_email("")
    ('', '')
    >>> extract_name_email(" ")
    ('', '')
    """

    text = text.strip()
    if "@" not in text:
        return text, ""

    name, email = parseaddr(text)
    if name and email:
        return name, email

    # Wrap the email address with angle brackets and try again
    text = re.sub(r"^(.+)\s(.+@.+)$", r"\g<1> <\g<2>>", text)
    return parseaddr(text)
