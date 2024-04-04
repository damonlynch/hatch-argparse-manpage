# SPDX-FileCopyrightText: Copyright 2024 Damon Lynch <damonlynch@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from hatchling.plugin import hookimpl
from hatch_argparse_manpage.plugin import ArgparseManpageBuildHook


@hookimpl
def hatch_register_build_hook():
    return ArgparseManpageBuildHook
