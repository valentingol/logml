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
from logml._version import __version__, __version_tuple__
from logml.logger import Logger

__all__ = ['__version__', '__version_tuple__', 'Logger']
