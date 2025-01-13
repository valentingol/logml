# Copyright (c) 2023 Valentin Goldite. All Rights Reserved.
"""Logger class."""
import atexit
import re
import time
from typing import Any, Dict, Iterable, List, Optional, Union

from rich.console import Group
from rich.live import Live
from rich.table import Table
from rich.text import Text

from logml import RICH_CONSOLE
from logml.time_utils import get_time_range, sec_to_timestr

VarType = Union[int, float, str, bool]
DictVarType = Union[Dict[str, int], Dict[str, float], Dict[str, str], Dict[str, bool]]


class Logger:
    """Logger class. Handles int, float, str and bool values.

    Parameters
    ----------
    n_epochs : int
        Number of epochs.
    n_batches : Optional[int]
        Number of batches per epoch. Set to None if not available.
    log_interval : int, optional
        Number of batches between each log. None for 4 update per second.
        By default 1.
    name: Optional[str], optional
        Name of the logger. It will be display at the top of the logs.
        By default None (no name).
    styles : Union[Dict, str], optional
        Default style of the values. Include color, bold, italic and more
        See https://rich.readthedocs.io/en/stable/style.html for more details.
        E.g. {'loss': 'bold red', 'acc': 'italic #af00ff'}
        Use a single string to apply the same style to all values.
        These styles can also be set or overwritten in the log method.
        By default, use rich default style.
    sizes : Union[Dict, int], optional
        Default sizes to display for each numerical values.
        Note that the dot is counted as a character.
        E.g. {'loss': 3, 'acc': 2}.
        Use a single int to apply the same size to all values.
        These numbers can also be set or overwritten in the log method.
        By default 6.
    average : Optional[List[str]], optional
        Default list of the values to average over the epoch.
        This can also be overwritten in the log method.
        By default None.
    silent : bool, optional
        Whether to print the logs or not. By default False.
    show_bar : bool, optional
        Whether to show the progress bar or not. By default True.
    show_time : bool, optional
        Whether to show the time or not. By default True.
    bold_keys : bool, optional
        Whether to bold the key or not. By default False.
    name_style: str, optional
        Style of the name. By default, use the rich default style.

    Examples
    --------
    ::

        logger = Logger(n_epochs=10, n_batches=100)
        for _ in range(10):
            for _ in logger.tqdm(range(100)):
                logger.log(loss=0.5, acc=0.9)

    Attribute
    ---------
    step : int
        Number of batches seen since the beginning.
    current_epoch : int
        Current epoch number (starting at 1).
    current_batch : int
        Current batch number (starting at 1).
    vals : Dict[str, VarType]
        Last values called inside log (not averaged nor resized).
    mean_vals : Dict[str, VarType]
        Current mean values (only numerical values).
    """

    def __init__(
        self,
        n_epochs: int,
        n_batches: Optional[int],
        log_interval: Optional[int] = 1,
        name: Optional[str] = None,
        *,
        styles: Union[Dict, str] = "",
        sizes: Union[Dict, int] = 6,
        average: Optional[List[str]] = None,
        silent: bool = False,
        show_bar: bool = True,
        show_time: bool = True,
        bold_keys: bool = False,
        name_style: str = "",
    ) -> None:
        # Log parameters
        self.silent = silent
        self.name = name
        self.show_bar = show_bar
        self.show_time = show_time
        self.bold_keys = bold_keys
        # Default log configs
        self.name_style = name_style
        self._default_styles = styles
        self._default_sizes = sizes
        self._default_average: Dict = {key: True for key in average} if average else {}
        # Internal variables
        self.n_epochs = n_epochs
        self.n_batches = n_batches
        self.log_interval = log_interval
        self.step = 0
        self._glob_time = 0.0  # Updated with .start() method
        self._epoch_time = 0.0
        self.current_epoch = 0
        self.current_batch = 0
        self._on_tqdm = False
        self._just_new_epoch = False
        self._pause_time = -1.0  # Time when pause is called (-1 if not paused)
        self._delta_pause_time = 0.0  # Time elapsed between pause and resume
        # Internal values
        self.vals: Dict = {}  # Last vals called inside log
        self._counts: Dict = {}
        self.mean_vals: Dict = {}  # Current mean vals
        # Rich elements
        self.live = Live(
            renderable=None,
            console=RICH_CONSOLE,
            refresh_per_second=4,
            auto_refresh=False,
        )
        self._renderable = None
        self.console = RICH_CONSOLE
        # Table and message infos from the previous log of the same batch
        self._prev_tables_list: List[Table] = []
        self._prev_table_width = 0
        self._prev_row: List[Text] = []
        self._prev_flat_cell = True
        self._prev_message = ""
        # Force live display to end at exit
        atexit.register(self.stop)
        # Start
        self.start()  # Now, self._glob_time = time.time()

    def start(self) -> None:
        """Set the start time of the training (already called at initialization)."""
        self._glob_time = self.get_current_time()

    def log(
        self,
        values: Optional[Dict[str, VarType]] = None,
        *,
        message: str = "",
        styles: Union[Dict[str, str], str, None] = None,
        sizes: Union[Dict[str, int], int, None] = None,
        average: Optional[List[str]] = None,
    ) -> None:
        """Log the values with style.

        Parameters
        ----------
        values : Dict[str, Any] | None
            Values to log. E.g. {'loss': 0.1, 'acc': 0.9}
        message : str, optional
            Message to display at the end of the log. By default empty.
        styles : Union[Dict, str, None], optional
            Style of the values. Include color, bold, italic and more
            See https://rich.readthedocs.io/en/stable/style.html for more details.
            E.g.::

                {'loss': 'bold red', 'acc': 'italic #af00ff'}

            Use a single string to apply the same style to all values.
            By default None (use the default style).
        sizes : Union[Dict, int], optional
            Size of the values to display for each numerical values.
            E.g.::

                {'loss': 7, 'acc': 2}

            Use a single int to apply the same size to all values.
            By default None (use the default style).
        average : Optional[List[str]], optional
            List of the values to average over the epoch.
            None to not average. By default None.
        """
        self._prelog_check()
        values = {} if values is None else values
        # Update internal values
        for key, val in values.items():
            self._update_val(key, val)
        # Never log if silent
        if self.silent:
            return

        # Update the live display

        renderables = []

        # Add Name (if exists)
        if self.name:
            renderables.append(self._build_name())
        # Add epoch and batch info line
        renderables.append(self._build_epoch_batch())
        # Add bar (if activated)
        if self.show_bar:
            renderables.append(self._build_bar())
        # Build time info (if activated)
        if self.show_time:
            renderables.append(self._build_time_info())
        # Build keys and values table
        if len(values) > 0:
            average_dict = {key: True for key in average} if average else {}
            vals_table = self._build_keys_vals(
                values,
                styles=styles,  # type: ignore
                sizes=sizes,  # type: ignore
                average=average_dict,
            )
            renderables.append(vals_table)
        # Build message (if exists)
        if message or self._prev_message:
            renderables.append(self._build_message(message))

        # Create renderable group and update the live display
        self._renderable = Group(*renderables)
        refresh = (
            # auto refresh regularly if no log interval
            self.log_interval is None
            # refresh at log intervals
            or self.current_batch % self.log_interval == 0
            # refresh at first batch
            or self.current_batch == 1
            # refresh at last batch (if n_batches is specified)
            or (self.n_batches and self.current_batch == self.n_batches)
        )

        self.live.update(renderable=self._renderable, refresh=refresh)

    def tqdm(
        self,
        iterable: Iterable,
        *,
        reset_means: bool = True,
    ) -> Any:
        """Browse an iterable dataset and automatically update the epoch and batch.

        No need to explicitly call :meth:`new_epoch` or :meth:`new_batch` as
        they are automatically called. If :attr:`n_batches` is not specified and
        the iterable implement a `__len__` attribute, the number of batch is
        inferred and store in :attr:`n_batches`.

        Parameters
        ----------
        iterable : Iterable
            Iterable dataset.
        reset_means: bool, optional
            Whether to reset the computed mean values at the start of the epoch.
            By default True.
        """
        if self.n_batches is None and hasattr(iterable, "__len__"):
            self.n_batches = len(iterable)  # type: ignore
        self.new_epoch(reset_means=reset_means)
        for batch in iterable:
            self.new_batch()
            self._on_tqdm = True
            yield batch
            self._on_tqdm = False
        self.stop()

    def new_epoch(
        self,
        *,
        reset_means: bool = True,
    ) -> None:
        """Declare a new epoch.

        Parameters
        ----------
        reset_means: bool, optional
            Whether to reset the computed mean values at the start of the epoch.
            By default True.
        """
        if self._just_new_epoch:
            return
        self._just_new_epoch = True
        # Reset internal variables
        if reset_means:
            self._counts = {key: 0 for key in self._counts}
            self.mean_vals = {key: 0 for key in self.mean_vals}
        self.live = Live(
            renderable=None,
            console=RICH_CONSOLE,
            refresh_per_second=4,
            auto_refresh=False,
        )
        self._renderable = None
        # "Detach" the logs from the previous epoch
        self.detach()
        # Update epoch and batch
        self.current_epoch += 1
        self.current_batch = 0
        # Start the new live display
        self.live.start()
        # Set the new epoch start time
        self._epoch_time = self.get_current_time()

    def start_epoch(self, *, reset_means: bool = True) -> None:
        """Declare a new epoch. Alias for :meth:`new_epoch`."""
        self.new_epoch(reset_means=reset_means)

    def new_batch(self) -> None:
        """Declare a new batch."""
        # No longer just new epoch
        self._just_new_epoch = False
        # On tqdm context, the batch is automatically incremented
        if not self._on_tqdm:
            self.step += 1
            self.current_batch += 1
        # Reset the previous table info
        self._prev_tables_list = []
        self._prev_table_width = 0
        self._prev_row = []
        self._prev_flat_cell = True
        self._prev_message = ""

    def start_batch(self) -> None:
        """Declare a new batch. Alias for :meth:`new_batch`."""
        self.new_batch()

    def detach(self, *, skipline: bool = True) -> None:
        """Stop the live display.

        Stop the live display while keeping the current display visible in
        the terminal.

        Note
        ----
            Calling :meth:`detach` or :meth:`stop` is necessary to print something
            at the end of an epoch. Otherwise, the print will be shown above
            the live display.
        """
        if self.console._live is not None:  # pylint: disable=protected-access
            self.console._live.stop()  # pylint: disable=protected-access
            self.console.clear_live()
        if not self.silent and skipline:
            self.console.print("")

    def stop(self) -> None:
        """Stop the live display.

        Stop the live display while keeping the current display visible in
        the terminal. Alias for :meth:`detach` with `skipline=False`.

        Note
        ----
            Calling :meth:`stop` or :meth:`detach` is necessary to print something
            at the end of an epoch. Otherwise, the print will be shown above
            the live display.
        """
        self.detach(skipline=False)

    def pause(self) -> None:
        """Pause the current time."""
        self._pause_time = time.time()

    def resume(self) -> None:
        """Resume the current time if paused."""
        if self._pause_time > 0.0:
            # Update total time spent in pause periods
            self._delta_pause_time += time.time() - self._pause_time
            self._pause_time = -1.0

    def get_current_time(self) -> float:
        """Get the current time. Take into account the pause periods."""
        # If currently paused, use the pause time
        current_time = time.time() if self._pause_time < 0.0 else self._pause_time
        # Subtract delta_current_time to get the time ignoring
        # the time spent during pause/resume periods
        return current_time - self._delta_pause_time

    def reset(self) -> None:
        """Reset the logger as at initialization."""
        self.stop()
        self.step = 0
        self._epoch_time = 0.0
        self.current_epoch = 0
        self.current_batch = 0
        self._on_tqdm = False
        self._pause_time = -1.0
        self._delta_pause_time = 0.0
        self.vals = {}
        self.mean_vals = {}
        self._counts = {}
        self.live = Live(
            renderable=None,
            console=RICH_CONSOLE,
            refresh_per_second=4,
            auto_refresh=False,
        )
        self._renderable = None
        self._prev_tables_list = []
        self._prev_table_width = 0
        self._prev_row = []
        self._prev_flat_cell = True
        self._prev_message = ""
        # Start
        self.start()  # Now, self._glob_time = time.time()

    def get_vals(self, *, average: Optional[List[str]] = None) -> Dict[str, VarType]:
        """Get the last values called with log, optionally averaged.

        Parameters
        ----------
        average : List[str], optional
            List of keys to return average. Support regex expressions.
            None for no averaged value. By default None.

        Returns
        -------
        Dict[str, VarType]
            Last values called with log (optionally averaged).
        """
        if average is None:
            average = []
        vals = self.vals.copy()
        for key in vals:
            if key in average:
                vals[key] = self.mean_vals[key]
            else:
                for pattern in average:
                    if re.match(pattern, key):
                        vals[key] = self.mean_vals[key]
        return vals

    def _prelog_check(self) -> None:
        """Check if the logger is ready to log."""
        err_message = ""
        if self.current_epoch == 0:
            err_message += (
                "You must indicate a new epoch before logging "
                "with `logger.new_epoch()` at start of the epoch.\n"
            )
        if self.current_batch == 0:
            err_message += (
                "You must indicate a new batch before logging "
                "with `logger.new_batch()` just after batch loading.\n"
            )
        if err_message:
            err_message += (
                "Otherwise, you can use `for batch in logger.tqdm(dataset):` "
                "in the batch loop."
            )
            raise ValueError(err_message)

    def _update_val(self, key: str, val: VarType) -> None:
        """Update the internal values."""
        if key not in self._counts:
            self._counts[key] = 0
        if key not in self.mean_vals:
            self.mean_vals[key] = 0
        self._counts[key] += 1
        if isinstance(val, (int, float)):
            mean = (self.mean_vals[key] * (self._counts[key] - 1) + val) / self._counts[
                key
            ]
            self.mean_vals[key] = mean
        self.vals[key] = val

    def _build_name(self) -> Text:
        """Build the name of the logger."""
        return Text(text=self.name, style=self.name_style)

    def _build_epoch_batch(self) -> Text:
        """Build a text containing epoch and batch info."""
        if self.n_batches is not None:
            return Text(
                f"Epoch {self.current_epoch}/{self.n_epochs}, "
                f"batch {self.current_batch}/{self.n_batches}",
            )
        # Unknown number of batches
        return Text(
            f"Epoch {self.current_epoch}/{self.n_epochs}, "
            f"batch {self.current_batch}",
        )

    def _build_bar(self) -> Text:
        """Build a text containing a custom progress bar."""
        if self.n_batches is not None:
            progress = min(100, int(100 * self.current_batch / self.n_batches))
            arrow_len = int(47 * progress / 100)
            arrowhead = ">" if arrow_len < 47 else "="
            return Text(
                f"[{'=' * arrow_len}{arrowhead}{' ' * (47-arrow_len)}]"
                f"[{progress:3d}%]",
                overflow="ellipsis",
            )
        # NOTE: We don't know the number of batches, so we just print
        # a bar that cycles every 20 log intervals or every 100 batches
        # if log_interval is None.
        if self.log_interval:
            progress = (self.step // self.log_interval) % 20
            arrow_len = int(54 * progress / 19)
        else:
            arrow_len = int(54 * (self.step % 100) / 99)
        bar_list = [" "] * 54
        for i in range(3):
            bar_list[(arrow_len + i) % 54] = "="
        return Text(f"[{''.join(bar_list)}]", overflow="ellipsis")

    def _build_time_info(self) -> Text:
        """Build time info text."""
        (delta_glob, delta_epoch, eta_glob, eta_epoch) = get_time_range(
            current_time=self.get_current_time(),
            start_glob=self._glob_time,
            start_epoch=self._epoch_time,
            current_epoch=self.current_epoch,
            current_batch=self.current_batch,
            n_epochs=self.n_epochs,
            n_batches=self.n_batches,
        )
        delta_glob_str = sec_to_timestr(delta_glob)
        delta_epoch_str = sec_to_timestr(delta_epoch)
        eta_glob_str = sec_to_timestr(eta_glob) if eta_glob is not None else " ? "
        eta_epoch_str = sec_to_timestr(eta_epoch) if eta_epoch is not None else " ? "
        time_str = (
            f"[global {delta_glob_str} < {eta_glob_str} | "
            f"epoch {delta_epoch_str} < {eta_epoch_str}]"
        )
        return Text(time_str, overflow="ellipsis")

    def _build_keys_vals(
        self,
        values: Dict[str, VarType],
        *,
        styles: Union[Dict[str, str], str],
        sizes: Union[Dict[str, int], int],
        average: Union[Dict[str, bool], bool],
    ) -> Group:
        """Build a group of tables containing the keys and values."""
        # flat_cell = True => log "key: value"
        # flat_cell = False => log "key \n value"
        if not self._prev_tables_list:
            # No previous logged values in same epoch
            # => Adapt flat_cell to number of values
            flat_cell = len(values) < 3
        else:
            # Previous logged values in same epoch => keep same flat_cell
            flat_cell = self._prev_flat_cell

        # The row contains all the values of the last table (if any)
        tables_list = self._prev_tables_list[:-1]
        row = self._prev_row
        table_width = self._prev_table_width

        # New table
        tables_list.append(Table(show_header=False, show_edge=False))

        for key, val in values.items():
            # Get style, size and average bool
            style = self._get_param(
                key,
                styles,
                self._default_styles,
                default_value="",
            )
            size = self._get_param(key, sizes, self._default_sizes, default_value=6)
            avg = self._get_param(
                key, average, self._default_average, default_value=False
            )
            # Format value and get average if needed
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                if avg:
                    val = self.mean_vals[key]
                val = str(val)
                # Keep exp notation if needed
                exp_ind = val.index("e") if "e" in val else len(val)
                size = min(int(size), exp_ind)
                val = val[:size].ljust(size) + val[exp_ind:]
            # cell_width: expected length of the cell to be shown
            if flat_cell:
                cell_width = 3 + len(str(key)) + len(str(val))
            else:
                cell_width = 3 + max(len(str(key)), len(str(val)))
            # Create a new table when the current table is too wide
            if table_width + cell_width > self.console.width:
                tables_list[-1].add_row(*row)
                tables_list.append(Table(show_header=False, show_edge=False))
                table_width = 0
                row = []
            cell = Text(justify="center")
            # Add key and value on the cell
            key_style = str(style) + " bold" if self.bold_keys else style
            cell.append(str(key), style=key_style)
            if flat_cell:
                cell.append(": " + str(val), style=style)
            else:
                cell.append("\n" + str(val), style=style)
            row.append(cell)
            table_width += cell_width
        # Add the last row
        tables_list[-1].add_row(*row)
        # Store the tables, last row and its width for the next log of the same batch
        self._prev_tables_list = tables_list
        self._prev_table_width = table_width
        self._prev_row = row
        self._prev_flat_cell = flat_cell
        return Group(*tables_list)

    @staticmethod
    def _get_param(
        key: str,
        log_configs: Union[DictVarType, VarType, None],
        default_configs: Union[DictVarType, VarType],
        *,
        default_value: VarType,
    ) -> VarType:
        """Get the parameter for the key on log_configs or default_configs."""
        if isinstance(log_configs, (int, float, str, bool)):
            return log_configs
        if log_configs is not None:  # logs_configs is a dict
            val = _regex_looking(key, log_configs)
            if val:
                return val
        # logs_configs is None => use default_configs
        if isinstance(default_configs, (int, float, str, bool)):
            return default_configs
        val = _regex_looking(key, default_configs)
        if val:
            return val
        return default_value

    def _build_message(self, message: str) -> Text:
        """Build message."""
        if not message and self._prev_message:
            # No current message but previous message => keep previous message
            message = self._prev_message
        else:
            self._prev_message = message
        return Text(message, justify="left")


def _regex_looking(key: str, config: DictVarType) -> Optional[VarType]:
    """Look on config (dict) for pattern matching and return the value."""
    if key in config:
        return config[key]
    val = None
    for pattern in config:
        if re.match(pattern, key):
            val = config[pattern]
    return val
