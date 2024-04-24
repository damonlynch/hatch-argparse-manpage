% hatch-argparse-manpage(3) | Hatch build hook plugin to generate manual pages

# NAME

hatch-argparse-manpage

# SYNOPSIS

Modify pyproject.toml:

```
[build-system]
requires = ["hatchling", "hatch-argparse-manpage"]
build-backend = "hatchling.build"

[tool.hatch.build.hooks.argparse-manpage]
manpages = ["MANPAGE-BUILD-CONFIGURATION", ...]
include-url = BOOLEAN
force-command-line = BOOLEAN
```

# DESCRIPTION

**Hatch-argparse-manpage** provides a build hook plugin for Hatch to automatically generate a
manual page from a _ArgumentParser_ object, using the Python program 
_argparse-manpage_.

## Directory layout
This plugin requires the directories storing the generated man pages are 
within the project's base directory, and are not equal to the project's base 
directory.

For example, for a project named _myproject_, and a src layout
_src/myproject_, an acceptable directory in which to store a
man page would be _man_.

## Required key value

`manpages`

: An array of strings specifying the build configuration for the man pages 
to be generated, using the format required by _argparse-manpage_.

## Optional key values

`include-url`

: Boolean specifying whether to show the project URL in 
the generated man page. The default is _true_.  See below.

`force-command-line`

:  Boolean specifying whether to invoke _argparse-manpage_ from the command 
line or by calling it as a Python object. The default is _false_. See below.

## Project URLs
If a URL is not specified in the man page's build configuration, this plugin
extracts it from the _\[project.urls]_ section of the project's _pyproject.toml_:

1. If a homepage URL is specified, then it is used.
2. If not, if only one URL is specified, it is used.

Argparse-manpage uses a project URL to 
generate a man section that explains where to download the program the 
page is being built for. See above to suppress inclusion of the URL in the 
man page.

## Argparse-manpage invocation

This plugin defaults to calling _argparse-manpage's_ Python code directly. If 
this generates an exception, this plugin will attempt to call argparse-manpage 
as a command line program. See above to override this behaviour using 
the optional key _force-command-line_.

## Cleaning output files

This plugin includes logic to remove the files it outputs using hatch's
`clean` hook. As well as individual files, any output directories created 
will also be removed, as long as these directories do not contain files 
created by something other than this plugin.

# EXAMPLES

Generate three manpages:
```toml
[tool.hatch.build.hooks.argparse-manpage]
manpages = [
    "man/foo.1:object=parser:pyfile=bin/foo.py",
    "man/bar.1:function=get_parser:pyfile=bin/bar",
    "man/baz.1:function=get_parser:pyfile=bin/bar:prog=baz",
]
```

Suppress the inclusion of the project URL:
```toml
[tool.hatch.build.hooks.argparse-manpage]
include-url = false
manpages = [
    "man/foo.1:object=parser:pyfile=bin/foo.py",
]
```

Force invoking argparse-manpage via the command line:
```toml
[tool.hatch.build.hooks.argparse-manpage]
force-command-line = true
manpages = [
    "man/foo.1:object=parser:pyfile=bin/foo.py",
]
```

# HISTORY 

This plugin is not an official project of
argparse-manpage.
Instead, it acts as a wrapper around it, making it available to Hatch users.
As such, if argparse-manpage changes in ways incompatible with this 
plugin, this plugin may not function as expected.

This plugin has been tested against argparse-manpage version 4.5.

The code to parse the _pyproject.toml_ config in this plugin overlaps with
the code in _argparse-manpage_,
but differs in that it is rewritten to conform to contemporary Python 
stylistic conventions, as well as the specific needs of this plugin.

# SEE ALSO

argparse-manpage

# AUTHOR

Damon Lynch <damonlynch@gmail.com>

# COPYRIGHT

Copyright 2024 Damon Lynch.
