#  SPDX-FileCopyrightText: 2024-2026 Damon Lynch <damonlynch@gmail.com>
#  SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from hatch_argparse_manpage.plugin import extract_name_email


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Damon Lynch <damonlynch@gmail.com>", ("Damon Lynch", "damonlynch@gmail.com")),
        ("Damon Lynch damonlynch@gmail.com", ("Damon Lynch", "damonlynch@gmail.com")),
        ("Damon Lynch", ("Damon Lynch", "")),
        ("damonlynch@gmail.com", ("", "damonlynch@gmail.com")),
        ("", ("", "")),
        (" ", ("", "")),
    ],
)
def test_extract_name_email(text: str, expected: tuple[str, str]) -> None:
    assert extract_name_email(text) == expected
