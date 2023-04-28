
# LoggerML - Machine Learning Logger in the console

Log your Machine Learning training in the console in a beautiful way using
[rich](https://github.com/Textualize/rich)✨ with useful information but with
minimal code.

[![Release](https://img.shields.io/github/v/release/valentingol/logml?include_prereleases)](https://github.com/valentingol/logml/releases)
![PythonVersion](https://img.shields.io/badge/python-3.8%20%7E%203.11-informational)
[![License](https://img.shields.io/github/license/valentingol/logml?color=999)](https://stringfixer.com/fr/MIT_license)

[![Ruff_logo](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)
[![Black_logo](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![Ruff](https://github.com/valentingol/logml/actions/workflows/ruff.yaml/badge.svg)](https://github.com/valentingol/logml/actions/workflows/ruff.yaml)
[![Flake8](https://github.com/valentingol/logml/actions/workflows/flake.yaml/badge.svg)](https://github.com/valentingol/logml/actions/workflows/flake.yaml)
[![Pydocstyle](https://github.com/valentingol/logml/actions/workflows/pydocstyle.yaml/badge.svg)](https://github.com/valentingol/logml/actions/workflows/pydocstyle.yaml)
[![MyPy](https://github.com/valentingol/logml/actions/workflows/mypy.yaml/badge.svg)](https://github.com/valentingol/logml/actions/workflows/mypy.yaml)
[![PyLint](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/valentingol/451f91cece4478ebc81377e27e432f8b/raw/logml_pylint.json)](https://github.com/valentingol/logml/actions/workflows/pylint.yaml)

[![Tests](https://github.com/valentingol/logml/actions/workflows/tests.yaml/badge.svg)](https://github.com/valentingol/logml/actions/workflows/tests.yaml)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/valentingol/451f91cece4478ebc81377e27e432f8b/raw/logml_tests.json)](https://github.com/valentingol/logml/actions/workflows/tests.yaml)

## Installation

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

## Quick start

Integrate the LogML logger in your training loop. For instance for 4 epochs,
20 batches per epoch and a log interval of 2 batches:

```python
from logml import Logger

logger = Logger(
    n_epochs=4,
    n_batches=20,
    log_interval=2,
)
for _ in range(4):
    logger.start_epoch()  # Indicate the start of a new epoch
    for _ in range(20):
        logger.start_batch()  # Indicate the start of a new batch
        logger.log({'loss': 0.54321256, 'accuracy': 0.85244777})
```

Yields:

```script
Epoch 1/4, batch 20/20
[================================================][100%]
[global 00:00:02 > 00:00:06 | epoch 00:00:02 > 00:00:00]
loss: 0.5432 | accuracy: 0.8524 |

Epoch 2/4, batch 8/20
[=================>                              ][40%]
[global 00:00:03 > 00:00:05 | epoch 00:00:01 > 00:00:01]
loss: 0.5432 | accuracy: 0.8524 |
```

Now you can customize the logger with your own styles and colors. You can set the default configuration at the initialization of the logger and then you can override it during log. For instance:

```python
logger = Logger(
    n_epochs=4,
    n_batches=20,
    # (Log interval by default is 1, log every batch)
    styles='yellow',
    digits={'accuracy': 2},
    average=['loss'],  # loss will be averaged over the current epoch
    bold_keys=True,
    show_time=False,  # Remove the time bar
)
for _ in range(4):
    logger.start_epoch()
    for _ in range(20):
        logger.start_batch()
        # Overwrite the default style for "loss" and add a message
        logger.log(
            {'loss': 0.54321256, 'accuracy': 85.244777},
            styles={'loss': 'italic red'},
            message="Training is going well?\nYes!",
        )
```

Yields:

```script
Epoch 1/4, batch 20/20
[================================================][100%]
loss: 0.5432 | accuracy: 85 |

Epoch 2/4, batch 7/20
[=================>                              ][35%]
[global 00:00:03 > 00:00:05 | epoch 00:00:01 > 00:00:01]
loss: 0.5432 | accuracy: 85 |
Training is going well?
Yes!
```

With "loss: 0.5432" in italic red, "accuracy: 85" in yellow and both keys in bold.


Finally, if you don't have the number of batches in advance, you can initialize the logger with `n_batches=None`. Only the available information will be displayed. For instance with the configuration of the first example:

```script
Epoch 1/4, batch 20/20
[  *                                             ][ ? %]
[global 00:00:02 >  ? | epoch 00:00:02 >  ? ]
loss: 0.5432 | accuracy: 0.8524 |

Epoch 2/4, batch 8/20
[                           *                     ][ ? %]
[global 00:00:03 > 00:00:05 | epoch 00:00:01 > 00:00:01]
loss: 0.5432 | accuracy: 0.8524 |
```

The progress bar is replaced by a cyclic animation. The eta times are not know at the first epoch but was estimated after the second epoch.

## Todo

- [ ] Manage a validation loop (then multiple loggers)
- [ ] Enable not using `new_epoch/log()` if log config is minimal
- [ ] Add color customization for message, epoch/batch number and time

## How to contribute

For **development**, install the package dynamically and dev requirements with:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

Everyone can contribute to LogML, and we value everyone’s contributions.
Please see our [contributing guidelines](CONTRIBUTING.md) for more information 🤗

## License

Copyright (C) 2023  Valentin Goldité

This program is free software: you can redistribute it and/or modify it under the
terms of the [MIT License](LICENSE). This program is distributed in the hope that
it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

This project is free to use for COMMERCIAL USE, MODIFICATION, DISTRIBUTION and
PRIVATE USE as long as the original license is include as well as this copy
right notice at the top of the modified files.
