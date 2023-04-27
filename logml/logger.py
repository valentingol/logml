"""Logger class."""

import time
from functools import partial
from typing import Dict, List, Optional, Union

import cursor
from rich.console import Console

from logml.time_utils import get_time_range, sec_to_timestr

VarType = Union[int, float, str, bool]
DictVarType = Union[Dict[str, int], Dict[str, float], Dict[str, str], Dict[str, bool]]


class Logger():
    """Logger class. Handles int, float, str and bool values.

    Parameters
    ----------
    n_epochs : int
        Number of epochs.
    n_batches : Optional[int]
        Number of batches per epoch. Set to None if not available.
    log_interval : int, optional
        Number of batches between each log. By default 1.
    styles : Union[Dict, str], optional
        Default style of the values. These styles can be set or
        overwritten in the log method. Include color, bold, italic and more
        See https://rich.readthedocs.io/en/stable/style.html for more details.
        E.g. {'loss': 'bold red', 'acc': 'italic #af00ff'}
        Use a single string to apply the same style to all values.
        By default 'white'.
    digits : Union[Dict, int], optional
        Default number of digits to display for each numerical values.
        Note that the dot is counted as a digit.
        These numbers can be set or overwritten in the log method.
        E.g. {'loss': 3, 'acc': 2}.
        Use a single int to apply the same number of digits to all values.
        By default 6.
    average : Optional[List[str]], optional
        Default list of the values to average over the epoch.
        This can be overwritten in the log method.
        By default None.
    silent : bool, optional
        Whether to print the logs or not. By default False.
    show_bar : bool, optional
        Whether to show the progress bar or not. By default True.
    show_time : bool, optional
        Whether to show the time or not. By default True.
    bold_keys : bool, optional
        Whether to bold the key or not. By default False.
    """

    def __init__(
        self,
        n_epochs: int,
        n_batches: Optional[int],
        log_interval: int = 1,
        *,
        styles: Union[Dict, str] = 'white',
        digits: Union[Dict, int] = 6,
        average: Optional[List[str]] = None,
        silent: bool = False,
        show_bar: bool = True,
        show_time: bool = True,
        bold_keys: bool = False,
    ) -> None:
        # Log parameters
        self.silent = silent
        self.show_bar = show_bar
        self.show_time = show_time
        # Default configs
        self.default_styles = styles
        self.default_digits = digits
        self.default_average: Dict = {key: True for key in average} if average else {}
        self.bold_keys = bold_keys
        # Internal variables
        self.n_epochs = n_epochs
        self.n_batches = n_batches
        self.log_interval = log_interval
        self.iter = 0
        self.start_glob = time.time()
        self.start_epoch = -1.0
        self.current_epoch = 0
        self.current_batch = 0
        self.last_log_lines = 0
        # Internal values
        self.vals: Dict = {}
        self.counts: Dict = {}
        self.mean_vals: Dict = {}
        # Rich print
        self._print = partial(Console().print, highlight=False, overflow='ellipsis')

    def start(self) -> None:
        """Start the training."""
        self.start_glob = time.time()

    def reset(self) -> None:
        """Reset the logger."""
        self.iter = 0
        self.start_glob = time.time()
        self.start_epoch = -1.0
        self.current_epoch = 0
        self.current_batch = 0
        self.vals = {}
        self.mean_vals = {}
        self.counts = {}

    def new_epoch(self, *, detach_log: bool = True) -> None:
        """Start a new epoch."""
        self.start_epoch = time.time()
        self.current_epoch += 1
        self.current_batch = 0
        self.counts = {key: 0 for key in self.counts}
        self.mean_vals = {key: 0 for key in self.mean_vals}
        # "Detach" the logs from the previous epoch
        if not self.silent and detach_log:
            self.last_log_lines = 0
            print()

    def new_batch(self) -> None:
        """Start a new batch."""
        self.iter += 1
        self.current_batch += 1

    def _prelog_check(self) -> None:
        """Check if the logger is ready to log."""
        err_message = ""
        if self.current_epoch == 0:
            err_message += ("You must indicate a new epoch before logging "
                            "with `logger.new_epoch()` at start of the epoch.\n")
        if self.current_batch == 0:
            err_message += ("You must indicate a new batch before logging "
                            "with `logger.new_batch()` just after batch loading.\n")
        if err_message:
            raise ValueError(err_message)

    def log(
        self,
        values: Dict[str, VarType],
        *,
        message: Optional[str] = None,
        styles: Union[Dict[str, str], str, None] = None,
        digits: Union[Dict[str, int], int, None] = None,
        average: Optional[List[str]] = None,
    ) -> None:
        """Log the values with style.

        Parameters
        ----------
        values : Dict[str, Any]
            Values to log. E.g. {'loss': 0.1, 'acc': 0.9}
        message : Optional[str], optional
            Message to display at the end of the log. By default None.
        styles : Union[Dict, str, None], optional
            Style of the values. Include color, bold, italic and more
            See https://rich.readthedocs.io/en/stable/style.html for more details.
            E.g. {'loss': 'bold red', 'acc': 'italic #af00ff'}
            Use a single string to apply the same style to all values.
            By default None (use the default style).
        digits : Union[Dict, int], optional
            Number of digits to display for each numerical values.
            E.g. {'loss': 3, 'acc': 2}.
            Use a single int to apply the same number of digits to all values.
            By default None (use the default style).
        average : Optional[List[str]], optional
            List of the values to average over the epoch.
            None to not average. By default None.
        """
        self._prelog_check()
        # Update internal values
        for key, val in values.items():
            self._update_val(key, val)
        # No log if it is not the moment
        if (self.silent  # Never log if silent
            or (self.current_batch % self.log_interval != 0
                and self.current_batch != 1  # Log the first batch
                and (self.n_batches is None
                     or self.current_batch != self.n_batches))):  # Log the last batch
            return

        # Here we log

        cursor.hide()  # Prevent cursor to blink
        # Move cursor to the beginning of the previous log
        if self.last_log_lines > 0:
            print(f"\x1B[{self.last_log_lines}A", end="")
        # Print epoch and batch info
        self._print_epoch_batch()
        # Print bar (if available)
        self._print_bar()
        # Print time info (when available)
        self._print_time_info()
        average_dict = {key: True for key in average} if average else {}
        for key, val in values.items():
            # Get style, digits and average
            style = self._get_param(
                key,
                styles,
                self.default_styles,
                default_value='white'
            )
            n_digit = self._get_param(
                key,
                digits,
                self.default_digits,
                default_value=6
            )
            avg = self._get_param(
                key,
                average_dict,
                self.default_average,
                default_value=False
            )
            # Print key and value
            # NOTE: ignore type because types are actually str for style,
            # int for n_digit and bool for avg as expected but mypy infer
            # VarType that is union of these (it was more convenient to make
            # a unified _get_param method)
            self._print_key_val(
                key,
                val,
                style=style,  # type: ignore
                n_digit=n_digit,  # type: ignore
                avg=avg  # type: ignore
            )
        # NOTE: Add clear line escape token to avoid overlapping
        print('\x1B[0K')
        # Print message (if available)
        self._print_message(message)
        # Update "last log lines" count
        self.last_log_lines = 2 + int(self.show_bar) + int(self.show_time)
        if message:
            self.last_log_lines += message.count('\n') + 1
        cursor.show()  # Restore cursor

    def _print_key_val(
        self,
        key: str,
        val: VarType,
        *,
        style: str,
        n_digit: int,
        avg: bool
    ) -> None:
        """Print the key and value."""
        # Print key
        if self.bold_keys:
            self._print(key, style='bold ' + style, end=': ', highlight=False)
        else:
            self._print(key, style=style, end=': ')
        # Print value
        if isinstance(val, (int, float)):
            if avg:
                val = self.mean_vals[key]
            val = str(val)[:n_digit].ljust(n_digit)
        self._print(val, style=style, highlight=False, end='')
        self._print(' | ', end='')

    @staticmethod
    def _get_param(
        key: str,
        log_configs: Union[DictVarType, VarType, None],
        default_configs: Union[VarType, Dict[str, VarType]],
        *,
        default_value: VarType
    ) -> VarType:
        """Get the parameter for the key on log_configs or default_configs."""
        if isinstance(log_configs, (int, float, str, bool)):
            config = log_configs
        elif log_configs and key in log_configs:
            config = log_configs[key]
        elif not isinstance(default_configs, Dict):
            config = default_configs
        elif isinstance(default_configs, Dict) and key in default_configs:
            config = default_configs[key]
        else:
            config = default_value
        return config

    def _update_val(self, key: str, val: VarType) -> None:
        """Update the internal values."""
        if key not in self.counts:
            self.counts[key] = 0
        if key not in self.mean_vals:
            self.mean_vals[key] = 0
        self.counts[key] += 1
        if isinstance(val, (int, float)):
            mean = ((self.mean_vals[key] * (self.counts[key]-1) + val)
                    / self.counts[key])
            self.mean_vals[key] = mean
        self.vals[key] = val

    def _print_epoch_batch(self) -> None:
        """Print epoch and batch info."""
        if self.n_batches is not None:
            self._print(f"Epoch {self.current_epoch}/{self.n_epochs}, "
                        f"batch {self.current_batch}/{self.n_batches}", end='')
        else:
            self._print(f"Epoch {self.current_epoch}/{self.n_epochs}, "
                        f"batch {self.current_batch}", end='')
        # NOTE: Add clear line escape token to avoid overlapping
        print('\x1B[0K')

    def _print_bar(self) -> None:
        """Print progress bar."""
        if self.show_bar and self.n_batches is not None:
            progress = min(100, int(100 * self.current_batch / self.n_batches))
            arrow_len = int(47 * progress / 100)
            arrowhead = '>' if arrow_len < 47 else '='

            self._print(f"[{'=' * arrow_len}{arrowhead}{' ' * (47-arrow_len)}]",
                        f"[{progress:3d}%]",
                        sep='', end='')

        elif self.show_bar and self.n_batches is None:
            # NOTE: We don't know the number of batches, so we just print
            # a bar that cycles every 20 log intervals
            progress = (self.iter // self.log_interval) % 20
            arrow_len = int(47 * progress / 19)
            arrowhead = '*'
            self._print(f"[{' ' * arrow_len}{arrowhead}{' ' * (47-arrow_len)}]",
                        "[ ? %]",
                        sep='', end='')

        # NOTE: Add clear line escape token to avoid overlapping
        print('\x1B[0K')

    def _print_time_info(self) -> None:
        """Print time info."""
        if self.show_time:
            (delta_glob, delta_epoch, eta_glob, eta_epoch) = get_time_range(
                current_time=time.time(),
                start_glob=self.start_glob,
                start_epoch=self.start_epoch,
                current_epoch=self.current_epoch,
                current_batch=self.current_batch,
                n_epochs=self.n_epochs,
                n_batches=self.n_batches,
            )
            delta_glob_str = sec_to_timestr(delta_glob)
            delta_epoch_str = sec_to_timestr(delta_epoch)
            eta_glob_str = sec_to_timestr(eta_glob) if eta_glob is not None else ' ? '
            eta_epoch_str = sec_to_timestr(eta_epoch)if eta_epoch is not None else ' ? '

            print(f"[global {delta_glob_str} > {eta_glob_str} "
                  f"| epoch {delta_epoch_str} > {eta_epoch_str}]", end='')
            # NOTE: Add clear line escape token to avoid overlapping
            print('\x1B[0K')

    def _print_message(self, message: Optional[str]) -> None:
        """Print message."""
        if message:
            for line in message.split('\n'):
                self._print(line, end='')
                # NOTE: Add clear line escape token to avoid overlapping
                print('\x1B[0K')
