"""LogML.

Copyright (C) 2023  Valentin Goldité

    This program is free software: you can redistribute it and/or modify
    it under the terms of the MIT License.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    This project is free to use for COMMERCIAL USE, MODIFICATION,
    DISTRIBUTION and PRIVATE USE as long as the original license is
    include as well as this copy right notice.
"""
# pylint: disable=wrong-import-position

from rich.console import Console

from logml._version import __version__, __version_tuple__

RICH_CONSOLE = Console()

from logml.logger import Logger  # noqa: E402

__all__ = ["__version__", "__version_tuple__", "Logger", 'RICH_CONSOLE']
