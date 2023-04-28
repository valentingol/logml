# Installation

In a new virtual environment, install simply the package via
[pipy](https://pypi.org/project/loggerml/):

```bash
pip install loggerml
```

## Supported platforms

This package assume that you are using a terminal that support ANSI escape sequences.
See [here](https://en.wikipedia.org/wiki/ANSI_escape_code#Platform_support) for
supported platforms. All Unix and Emacs distribution are supported as well as Windows
but only on some machine (Windows 11 seems to work but not Windows 10).

The quick test to know if your terminal support ANSI escape sequence is to run the
following command in your terminal:

```script
python -c "print('\x1B')"
```

It should print an *empty* line.
