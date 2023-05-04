"""Logger class."""
import atexit
import time
from typing import Dict, List, Optional, Union

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
        Number of batches between each log. By default 1.
    name: Optional[str], optional
        Name of the logger. It will be display at the top of the logs.
        By default None (no name).
    styles : Union[Dict, str], optional
        Default style of the values. Include color, bold, italic and more
        See https://rich.readthedocs.io/en/stable/style.html for more details.
        E.g. {'loss': 'bold red', 'acc': 'italic #af00ff'}
        Use a single string to apply the same style to all values.
        These styles can also be set or overwritten in the log method.
        By default 'white'.
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
    name_style: Optional[str], optional
        Style of the name. Ignored if name is None. By default white.
    """

    def __init__(
        self,
        n_epochs: int,
        n_batches: Optional[int],
        log_interval: Optional[int] = 1,
        name: Optional[str] = None,
        *,
        styles: Union[Dict, str] = "white",
        sizes: Union[Dict, int] = 6,
        average: Optional[List[str]] = None,
        silent: bool = False,
        show_bar: bool = True,
        show_time: bool = True,
        bold_keys: bool = False,
        name_style: Optional[str] = None,
    ) -> None:
        # Log parameters
        self.silent = silent
        self.name = name
        self.show_bar = show_bar
        self.show_time = show_time
        # Default configs
        self.name_style = name_style
        self.default_styles = styles
        self.default_sizes = sizes
        self.default_average: Dict = {key: True for key in average} if average else {}
        self.bold_keys = bold_keys
        # Internal variables
        self.n_epochs = n_epochs
        self.n_batches = n_batches
        self.log_interval = log_interval
        self.step = 0
        self.start_glob = 0.0
        self.start()  # Now, self.start_glob = time.time()
        self.start_epoch = 0.0
        self.current_epoch = 0
        self.current_batch = 0
        # Internal values
        self.vals: Dict = {}
        self._counts: Dict = {}
        self.mean_vals: Dict = {}
        # Rich elements
        self.live = Live(
            renderable=None,
            console=RICH_CONSOLE,
            refresh_per_second=4,
            auto_refresh=False,
        )
        self.renderable = None
        self.console = RICH_CONSOLE
        atexit.register(self.stop)

    def start(self) -> None:
        """Set the start time of the training (already called at initialization)."""
        self.start_glob = time.time()

    def reset(self) -> None:
        """Reset the logger as at initialization."""
        self.stop()
        self.step = 0
        self.start_glob = time.time()
        self.start_epoch = 0.0
        self.current_epoch = 0
        self.current_batch = 0
        self.vals = {}
        self.mean_vals = {}
        self._counts = {}
        self.live = Live(
            renderable=None,
            console=RICH_CONSOLE,
            refresh_per_second=4,
            auto_refresh=False,
        )
        self.renderable = None

    def new_epoch(self, *, reset_avg: bool = True) -> None:
        """Declare a new epoch."""
        self.start_epoch = time.time()
        self.current_epoch += 1
        self.current_batch = 0
        if reset_avg:
            self._counts = {key: 0 for key in self._counts}
            self.mean_vals = {key: 0 for key in self.mean_vals}
        # "Detach" the logs from the previous epoch
        self.detach()
        self.live = Live(
            renderable=None,
            console=RICH_CONSOLE,
            refresh_per_second=4,
            auto_refresh=False,
        )
        self.renderable = None
        # Start the new live display
        self.live.start()

    def detach(self, *, skipline: bool = True) -> None:
        """Stop the live display.

        Stop the live display while keeping the current display visible in
        the terminal.
        """
        if self.console._live is not None:  # pylint: disable=protected-access
            self.console._live.stop()  # pylint: disable=protected-access
            self.console.clear_live()
        if not self.silent and skipline:
            self.console.print('')

    def stop(self) -> None:
        """Stop the live display.

        Stop the live display while keeping the current display visible in
        the terminal. Alias for `detach(skipline=False)`.
        """
        self.detach(skipline=False)

    def new_batch(self) -> None:
        """Declare a new batch."""
        self.step += 1
        self.current_batch += 1

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
            raise ValueError(err_message)

    def log(
        self,
        values: Dict[str, VarType],
        *,
        message: Optional[str] = None,
        styles: Union[Dict[str, str], str, None] = None,
        sizes: Union[Dict[str, int], int, None] = None,
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
        sizes : Union[Dict, int], optional
            Size of the values to display for each numerical values.
            E.g. {'loss': 3, 'acc': 2}.
            Use a single int to apply the same size to all values.
            By default None (use the default style).
        average : Optional[List[str]], optional
            List of the values to average over the epoch.
            None to not average. By default None.
        """
        self._prelog_check()
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
        if message:
            renderables.append(self._build_message(message))

        # Create renderable group and update the live display
        self.renderable = Group(*renderables)
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
        self.live.update(renderable=self.renderable, refresh=refresh)

    def _update_val(self, key: str, val: VarType) -> None:
        """Update the internal values."""
        if key not in self._counts:
            self._counts[key] = 0
        if key not in self.mean_vals:
            self.mean_vals[key] = 0
        self._counts[key] += 1
        if isinstance(val, (int, float)):
            mean = (
                (self.mean_vals[key] * (self._counts[key] - 1) + val)
                / self._counts[key]
            )
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
        bar_list = [' '] * 54
        for i in range(3):
            bar_list[(arrow_len + i) % 54] = '●'
        return Text(f"[{''.join(bar_list)}]", overflow="ellipsis")

    def _build_time_info(self) -> Text:
        """Build time info text."""
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
        eta_glob_str = sec_to_timestr(eta_glob) if eta_glob is not None else " ? "
        eta_epoch_str = (
            sec_to_timestr(eta_epoch) if eta_epoch is not None else " ? "
        )
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
        tables_list = [Table(show_header=False, show_edge=False)]
        table_width = 0
        row: List[Text] = []
        for key, val in values.items():
            # Get style, size and average bool
            style = self._get_param(
                key, styles, self.default_styles, default_value='',
            )
            size = self._get_param(key, sizes, self.default_sizes, default_value=6)
            avg = self._get_param(
                key, average, self.default_average, default_value=False
            )
            # Format value and get average if needed
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                if avg:
                    val = self.mean_vals[key]
                val = str(val)[: int(size)].ljust(int(size))
            # cell_width: expected length of the cell to be shown
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
            cell.append('\n' + str(val), style=style)
            row.append(cell)
            table_width += cell_width
        # Add the last row
        tables_list[-1].add_row(*row)
        return Group(*tables_list)

    @staticmethod
    def _get_param(
        key: str,
        log_configs: Union[DictVarType, VarType, None],
        default_configs: Union[VarType, Dict[str, VarType]],
        *,
        default_value: VarType,
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

    def _build_message(self, message: str) -> Text:
        """Build message."""
        return Text(message, justify='left')
