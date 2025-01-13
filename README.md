
# LoggerML - Rich machine learning logger in the console

Log your Machine Learning training in the console in a beautiful way using
[rich](https://github.com/Textualize/rich)✨ with useful information but with
minimal code.

## Documentation [here](https://logml.readthedocs.io/en/latest/)

---

[![PyPI version](https://badge.fury.io/py/loggerml.svg)](https://badge.fury.io/py/loggerml)
![PythonVersion](https://img.shields.io/badge/python-3.7%20%7E%203.11-informational)
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
[![Documentation Status](https://readthedocs.org/projects/logml/badge/?version=latest)](https://logml.readthedocs.io/en/latest/?badge=latest)

## Installation

In a new virtual environment, install simply the package via
[pipy](https://pypi.org/project/loggerml/):

```bash
pip install loggerml
```

This package is supported on Linux, macOS and Windows.
It is also supported on Jupyter Notebooks.

## Quick start

### Minimal usage

Integrate the LogML logger in your training loops! For instance for 4 epochs
and 20 batches per epoch:

```python
import time

from logml import Logger

logger = Logger(n_epochs=4, n_batches=20)

for _ in range(4):
    for _ in logger.tqdm(range(20)):
        time.sleep(0.1)  # Simulate a training step
        # Log whatever you want (int, float, str, bool):
        logger.log({
            'loss': 0.54321256,
            'accuracy': 0.85244777,
            'loss name': 'MSE',
            'improve baseline': True,
        })
```

Yields:

![base-gif](https://raw.githubusercontent.com/valentingol/logml/main/docs/_static/base.gif))

Note that the expected remaining time of the overall train is displayed as well as
the one for the epoch. The logger also provides also the possibility to average the
logged values over an epoch or a full training.

### Pause and resume

You can also pause and resume the logger internal time with `logger.pause()` and
`logger.resume()`. You can check the internal time with `logger.get_current_time()`.
Note that the resume method continues the time from **the last pause**.
it means that if you pause the training logger at 10 seconds, then resume it
at 20 seconds, the logger will display 10 seconds of training time. The global and
the epoch time will be updated accordingly. You can also find examples in
the documentation.

### Save the logs

In Linux you can use `tee` to save the logs in a file and display them in the console.
However you need to use `unbuffer` to keep the style:

```bash
unbuffer python main.py --color=auto | tee output.log
```

See
[here](https://superuser.com/questions/352697/preserve-colors-while-piping-to-tee)
for details.

### Advanced usage

Now you can add a validation logger, customize the logger with your own styles
and colors, compute the average of some values over batch, add a dynamic
message at each batch, update the value only every some batches and more!

At initialization you can set default configuration for the logger that will be
eventually overwritten by the configuration passed to the `log` method.

An example with more features:

```python
train_logger = Logger(
    n_epochs=2,
    n_batches=20,
    log_interval=2,
    name='Training',
    name_style='dark_orange',
    styles='yellow',  # Default style for all values
    sizes={'accuracy': 4},  # only 4 characters for 'accuracy'
    average=['loss'],  # 'loss' will be averaged over the current epoch
    bold_keys=True,  # Bold the keys
)
val_logger = Logger(
    n_epochs=2,
    n_batches=10,
    name='Validation',
    name_style='cyan',
    styles='blue',
    bold_keys=True,
    show_time=False,  # Remove the time bar
)
for _ in range(2):
    train_logger.new_epoch()  # Manually declare a new epoch
    for _ in range(20):
        train_logger.new_batch()  # Manually declare a new batch
        time.sleep(0.1)
        # Overwrite the default style for "loss" and add a message
        train_logger.log(
            {'loss': 0.54321256, 'accuracy': 85.244777},
            styles={'loss': 'italic red'},
            message="Training is going well?\nYes!",
        )
    val_logger.new_epoch()
    for _ in range(10):
        val_logger.new_batch()
        time.sleep(0.1)
        val_logger.log({'val loss': 0.65422135, 'val accuracy': 81.2658775})
    val_logger.detach()  # End the live display to print something else after
```

Yields:

![Alt Text](https://raw.githubusercontent.com/valentingol/logml/main/docs/_static/advanced.gif)

### Don't know the number of batches in advance?

If you don't have the number of batches in advance, you can initialize the logger
with `n_batches=None`. Only the available information will be displayed. For instance
with the configuration of the first example:

![Alt Text](https://raw.githubusercontent.com/valentingol/logml/main/docs/_static/no_n_batches.png)

The progress bar is replaced by a cyclic animation. The eta times are not know at the
first epoch but was estimated after the second epoch.

Note that if you use `Logger.tqdm(dataset)` and the dataset has a length, the number of
batches will be automatically set to the length of the dataset.

## How to contribute

For **development**, install the package dynamically and dev requirements with:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

Everyone can contribute to LogML, and we value everyone’s contributions.
Please see our [contributing guidelines](CONTRIBUTING.md) for more information 🤗

### Todo

To do:

Done:

- [x] Allow multiple logs on the same batch
- [x] Finalize tests for 1.0.0 major release
- [x] Add docs sections: comparison with tqdm and how to use mean_vals
  (with exp tracker)
- [x] Use regex for `styles`, `sizes` and `average` keys
- [x] Be compatible with notebooks
- [x] Get back the cursor when interrupting the training
- [x] `logger.tqdm()` feature (used like `tqdm.tqdm`)
- [x] Doc with Sphinx
- [x] Be compatible with Windows and Macs
- [x] Manage a validation loop (then multiple loggers)
- [x] Add color customization for message, epoch/batch number and time
- [x] Add pause/resume feature

## License

Copyright (C) 2023  Valentin Goldité

This program is free software: you can redistribute it and/or modify it under the
terms of the [MIT License](LICENSE). This program is distributed in the hope that
it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

This project is free to use for COMMERCIAL USE, MODIFICATION, DISTRIBUTION and
PRIVATE USE as long as the original license is include as well as this copy
right notice at the top of the modified files.
