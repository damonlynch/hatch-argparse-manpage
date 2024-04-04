# Hatch Argparse Manpage

|         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Package | [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-argparse-manpage.svg)](https://pypi.org/project/hatch-argparse-manpage) [![PyPI - Version](https://img.shields.io/pypi/v/hatch-argparse-manpage.svg)](https://pypi.org/project/hatch-argparse-manpage)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Meta    | [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![GitButler](https://img.shields.io/badge/GitButler-%23B9F4F2?logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMzkiIGhlaWdodD0iMjgiIHZpZXdCb3g9IjAgMCAzOSAyOCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTI1LjIxNDUgMTIuMTk5N0wyLjg3MTA3IDEuMzg5MTJDMS41NDI5NSAwLjc0NjUzMiAwIDEuNzE0MDYgMCAzLjE4OTQ3VjI0LjgxMDVDMCAyNi4yODU5IDEuNTQyOTUgMjcuMjUzNSAyLjg3MTA3IDI2LjYxMDlMMjUuMjE0NSAxNS44MDAzQzI2LjcxOTcgMTUuMDcyMSAyNi43MTk3IDEyLjkyNzkgMjUuMjE0NSAxMi4xOTk3WiIgZmlsbD0iYmxhY2siLz4KPHBhdGggZD0iTTEzLjc4NTUgMTIuMTk5N0wzNi4xMjg5IDEuMzg5MTJDMzcuNDU3MSAwLjc0NjUzMiAzOSAxLjcxNDA2IDM5IDMuMTg5NDdWMjQuODEwNUMzOSAyNi4yODU5IDM3LjQ1NzEgMjcuMjUzNSAzNi4xMjg5IDI2LjYxMDlMMTMuNzg1NSAxNS44MDAzQzEyLjI4MDMgMTUuMDcyMSAxMi4yODAzIDEyLjkyNzkgMTMuNzg1NSAxMi4xOTk3WiIgZmlsbD0idXJsKCNwYWludDBfcmFkaWFsXzMxMF8xMjkpIi8%2BCjxkZWZzPgo8cmFkaWFsR3JhZGllbnQgaWQ9InBhaW50MF9yYWRpYWxfMzEwXzEyOSIgY3g9IjAiIGN5PSIwIiByPSIxIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgZ3JhZGllbnRUcmFuc2Zvcm09InRyYW5zbGF0ZSgxNi41NzAxIDE0KSBzY2FsZSgxOS44NjQxIDE5LjgzODMpIj4KPHN0b3Agb2Zmc2V0PSIwLjMwMTA1NiIgc3RvcC1vcGFjaXR5PSIwIi8%2BCjxzdG9wIG9mZnNldD0iMSIvPgo8L3JhZGlhbEdyYWRpZW50Pgo8L2RlZnM%2BCjwvc3ZnPgo%3D)](https://gitbutler.com/) [![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) [![GitHub Sponsors](https://img.shields.io/github/sponsors/damonlynch?logo=GitHub%20Sponsors&style=social)](https://github.com/sponsors/damonlynch) |

-----

This provides
a [build hook](https://hatch.pypa.io/latest/config/build/#build-hooks) plugin
for [Hatch](https://github.com/pypa/hatch) to automatically generate a
manual page from an `ArgumentParser` object,
using [argparse-manpage](https://github.com/praiskup/argparse-manpage)
by [Pavel Raiskup](https://github.com/praiskup).

**Table of Contents**

* [Hatch Argparse Manpage](#hatch-argparse-manpage)
  * [Explanation](#explanation)
  * [Configuration](#configuration)
    * [Calling the plugin](#calling-the-plugin)
    * [Generating the manual page](#generating-the-manual-page)
    * [Extra options](#extra-options)
  * [Cleaning output files](#cleaning-output-files)
  * [History](#history)
  * [Related Hatch plugin](#related-hatch-plugin)
  * [License](#license)

## Explanation

This plugin is not an official project of
[argparse-manpage](https://github.com/praiskup/argparse-manpage).
Instead, it acts as a wrapper around it, making it available to Hatch users.
As such, if `argparse-manpage` changes in ways incompatible with this 
plugin, this plugin may not function as expected.

## Configuration

The [build hook plugin](https://hatch.pypa.io/latest/plugins/build-hook/)
name is `argparse-manpage`.

### Calling the plugin

Modify `pyproject.toml` to include the plugin as a build dependency:

```toml
[build-system]
requires = ["hatchling", "hatch-argparse-manpage"]
build-backend = "hatchling.build"
```

### Generating the manual page

This plugin requires the directory storing the generated man page is within the
project's base directory, and is not equal to the project's base directory.

For example, for a project named `myproject`, and a src layout
`src/myproject`, an acceptable directory in which to store the
manual page would be `man`.

Using the configuration option `[tool.hatch.build.hooks.argparse-manpage]`, 
specify the man pages using the format defined by 
[argparse-manpage](https://github.com/praiskup/argparse-manpage).
For example:
```toml
[tool.hatch.build.hooks.argparse-manpage]
manpages = [
    "man/foo.1:object=parser:pyfile=bin/foo.py",
    "man/bar.1:function=get_parser:pyfile=bin/bar",
    "man/baz.1:function=get_parser:pyfile=bin/bar:prog=baz",
]
```

### Extra options
By default, `argparse-manpage` uses a project URL passed to it to 
generate a manual section that explains where to download the program the 
page is being built for. To suppress this behavior, set `include-url`
to false.

This plugin defaults to calling `argparse-manpage`'s code directly. If this 
generates an exception, this plugin will attempt to call `argparse-manpage` 
as a command line program. To force the using `argparse-manpage` as a 
command line program, set force-command-line to true.

For example:
```toml
[tool.hatch.build.hooks.argparse-manpage]
include-url = false
force-command-line = true
manpages = [
    "man/foo.1:object=parser:pyfile=bin/foo.py",
    "man/bar.1:function=get_parser:pyfile=bin/bar",
    "man/baz.1:function=get_parser:pyfile=bin/bar:prog=baz",
]
```

## Cleaning output files

The plugin includes logic to remove the files it outputs using hatch's
`clean` hook. As well as individual files, any output directories created
will also be removed, as long as these directories do not contain files
created by something other than this plugin.

## History

The code to parse the pyproject.toml config in this plugin overlaps with
the code in [argparse-manpage](https://github.com/praiskup/argparse-manpage),
but differs in that it is rewritten to conform to contemporary Python 
stylistic conventions, as well as the specific needs of this plugin.

## Related Hatch plugin

GNU gettext users may be interested
in [hatch-gettext](https://github.com/damonlynch/hatch-gettext).

## License

`hatch-argparse-manpage` is distributed under the terms of
the [GPL-3.0-or-later](https://spdx.org/licenses/GPL-3.0-or-later.html) license.
