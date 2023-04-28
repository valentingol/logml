"""Test time_utils.py."""
from typing import Any, Mapping

import pytest_check as check

from logml.time_utils import get_time_range, sec_to_timestr


def test_get_time_range() -> None:
    """Test get_time_range."""
    params: Mapping[str, Any] = {
        "current_time": 4.0,
        "start_glob": 1.0,
        "start_epoch": 3.0,
        "current_epoch": 2,
        "current_batch": 5,
        "n_epochs": 4,
        "n_batches": 10,
    }
    (delta_glob, delta_epoch, eta_glob, eta_epoch) = get_time_range(
        current_time=4.0,
        start_glob=1.0,
        start_epoch=3.0,
        current_epoch=2,
        current_batch=5,
        n_epochs=4,
        n_batches=10,
    )
    check.equal(delta_glob, 3.0)
    check.equal(delta_epoch, 1.0)
    check.equal(eta_glob, 5.0)
    check.equal(eta_epoch, 1.0)

    (delta_glob, delta_epoch, eta_glob, eta_epoch) = get_time_range(
        current_time=4.0,
        start_glob=1.0,
        start_epoch=3.0,
        current_epoch=2,
        current_batch=5,
        n_epochs=4,
        n_batches=None,
    )
    check.equal(delta_glob, 3.0)
    check.equal(delta_epoch, 1.0)
    check.equal(eta_glob, 5.0)
    check.equal(eta_epoch, 1.0)

    (delta_glob, delta_epoch, eta_glob, eta_epoch) = get_time_range(
        current_time=4.0,
        start_glob=1.0,
        start_epoch=3.0,
        current_epoch=1,
        current_batch=5,
        n_epochs=4,
        n_batches=None,
    )
    check.equal(delta_glob, 3.0)
    check.equal(delta_epoch, 1.0)
    check.is_none(eta_glob)
    check.is_none(eta_epoch)

    for key in ["current_batch", "current_epoch", "n_epochs", "n_batches"]:
        with check.raises(ValueError):
            get_time_range(**{**params, key: 0})


def test_sec_to_timestr() -> None:
    """Test sec_to_timestr."""
    timestr = sec_to_timestr(499985.1)
    check.equal(timestr, "138:53:05")
    timestr = sec_to_timestr(-3.2)
    check.equal(timestr, "00:00:00")
