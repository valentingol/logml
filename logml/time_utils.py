"""Utilities for time data."""
from typing import Optional, Tuple


def sec_to_timestr(sec: float) -> str:
    """Return a string corresponding to the time given in seconds."""
    if sec <= 0.0:
        timestr = "00:00:00"
    else:
        sec_int = int(sec)
        timestr = f"{sec_int // 3600:02d}:{sec_int % 3600 // 60:02d}:{sec_int % 60:02d}"
    return timestr


def get_time_range(
    current_time: float,
    start_glob: float,
    start_epoch: float,
    current_epoch: int,
    current_batch: int,
    n_epochs: int,
    n_batches: Optional[int],
) -> Tuple[float, float, Optional[float], Optional[float]]:
    """Get delta and eta times for global and epoch.

    Parameters
    ----------
    current_time : float
        Current time in seconds.
    start_glob : float
        Global starting time in seconds.
    start_epoch : float
        Epoch starting time in seconds. None if not available.
    current_epoch : int, optional
        Current epoch (starting at 1). None if not available.
    current_batch : int, optional
        Current batch (starting at 1). None if not available.
    n_epochs : int, optional
        Number of epochs. None if not available.
    n_batches : Optional[int], optional
        Number of batches per epoch. None if not available. By default None.

    Raises
    ------
    ValueError
        If current_batch, current_epoch, n_epochs or n_batch are 0.

    Returns
    -------
    delta_glob : float
        Delta time since global start in seconds.
    delta_epoch : float
        Delta time since epoch start in seconds. None if unavailable.
    eta_glob : Optional[float]
        Estimated time until global end in seconds. None if unavailable.
    eta_epoch : Optional[float]
        Estimated time until epoch end in seconds. None if unavailable.
    """
    if current_batch == 0:
        raise ValueError("current_batch must be > 0")
    if current_epoch == 0:
        raise ValueError("current_epoch must be > 0")
    if n_epochs == 0:
        raise ValueError("n_epochs must be > 0")
    if n_batches == 0:
        raise ValueError("n_batches must be > 0 or None (if unavailable)")
    delta_glob = current_time - start_glob
    delta_epoch = current_time - start_epoch
    if n_batches is None:
        if current_epoch > 1:
            # one_epoch: time for one epoch (average over all completed epochs
            # since start)
            one_epoch = (delta_glob - delta_epoch) / (current_epoch - 1)
            eta_epoch = one_epoch - delta_epoch
            eta_glob = one_epoch * (n_epochs - current_epoch) + eta_epoch
        else:
            eta_epoch = None
            eta_glob = None
    else:
        eta_epoch = delta_epoch / current_batch * (n_batches - current_batch)
        # one_batch: time for one batch (average over all batches since start)
        one_batch = delta_glob / ((current_epoch - 1) * n_batches + current_batch)
        eta_glob = one_batch * n_batches * (n_epochs - current_epoch) + eta_epoch

    return (delta_glob, delta_epoch, eta_glob, eta_epoch)
