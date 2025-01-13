# Copyright (c) 2023 Valentin Goldite. All Rights Reserved.
"""Test logger.py."""
import time

import pytest
import pytest_check as check

from logml.logger import Logger


def test_logger() -> None:
    """Test Logger."""
    n_epochs = 3
    n_batches = 10
    logger = Logger(
        n_epochs=n_epochs,
        n_batches=n_batches,
        log_interval=2,
        sizes={"train acc": 2},
        styles="yellow",
        average=["train loss", "train acc"],
        bold_keys=True,
        name="Training",
        name_style="bold dark_orange",
    )
    logger.start()
    for i in range(2):
        for epoch in range(n_epochs):
            logger.start_epoch()
            for batch in range(n_batches):
                logger.start_batch()
                styles = {"train loss": "green", "train acc": "blue"}
                logger.log(
                    {
                        "train loss": 1 - int(100 * epoch / n_epochs) / 100,
                        "train acc": 100 - int(100 * batch / n_batches) / 100,
                        "loss name": "mse",
                        "best run": True,
                    },
                    message="This is...\nok?",
                    styles=styles,
                    average=["mse"],
                )
                logger.log({"additional loss": 0.05})
        if i == 0:
            logger.reset()
            logger.bold_keys = False
            logger.n_batches = None
    logger.log_interval = None
    logger.log(
        {f"new loss{i}": 0.4 for i in range(1, 16)},
        styles="red",
        sizes=3,
        message="\n",
    )

    with check.raises(ValueError):
        logger = Logger(2, 5)
        logger.log({"train loss": 1, "train acc": 1})
    with check.raises(ValueError):
        logger = Logger(2, 5)
        logger.new_epoch()
        logger.log({"train loss": 1, "train acc": 1})
    with check.raises(ValueError):
        logger = Logger(2, 5)
        logger.new_batch()
        logger.log({"train loss": 1, "train acc": 1})


def test_internal_values() -> None:
    """Test for internal values update."""
    logger = Logger(n_epochs=3, n_batches=2, average=["val2"])
    logger.new_epoch()
    logger.new_batch()
    logger.log({"val1": 1.0, "val2": 2.0})
    check.equal((logger.vals["val1"], logger.vals["val2"]), (1.0, 2.0))
    check.equal((logger.mean_vals["val1"], logger.mean_vals["val2"]), (1.0, 2.0))
    logger.new_batch()
    logger.log({"val1": 0.5, "val2": 1.0})
    check.equal((logger.vals["val1"], logger.vals["val2"]), (0.5, 1.0))
    check.equal((logger.mean_vals["val1"], logger.mean_vals["val2"]), (0.75, 1.5))
    logger.new_epoch()
    check.equal((logger.vals["val1"], logger.vals["val2"]), (0.5, 1.0))
    check.equal((logger.mean_vals["val1"], logger.mean_vals["val2"]), (0, 0))
    logger.new_batch()
    logger.log({"val1": 2.0, "val2": 1.0})
    check.equal((logger.vals["val1"], logger.vals["val2"]), (2.0, 1.0))
    check.equal((logger.mean_vals["val1"], logger.mean_vals["val2"]), (2.0, 1.0))
    logger.new_epoch(reset_means=False)
    logger.new_batch()
    logger.log({"val1": 1.0, "val2": 2.0})
    check.equal((logger.mean_vals["val1"], logger.mean_vals["val2"]), (1.5, 1.5))
    # Test get_vals
    check.equal(logger.get_vals(average=["val2"]), {"val1": 1.0, "val2": 1.5})
    check.equal(logger.get_vals(), {"val1": 1.0, "val2": 2.0})
    check.equal(logger.get_vals(average=["val.*"]), {"val1": 1.5, "val2": 1.5})

    logger.stop()


def test_silent(capsys: pytest.CaptureFixture) -> None:
    """Test silent logger."""
    captured = capsys.readouterr()
    logger = Logger(5, 5, name="Test", silent=True)
    for _ in range(5):
        logger.new_epoch()
        for _ in range(5):
            logger.new_batch()
            logger.log({"loss": 0.02})
    captured = capsys.readouterr()
    check.equal(captured.out, "")


def test_tqdm() -> None:
    """Test tqdm method."""
    n_epochs = 10
    n_batches = 10
    logger = Logger(n_epochs=n_epochs, n_batches=n_batches)
    for _ in range(10):
        logger.new_epoch()  # Should be avoided but should not raise error
        for _ in logger.tqdm(range(10)):
            logger.new_batch()  # Should be avoided but should not raise error
            logger.log({"loss": 0.02})
    logger = Logger(n_epochs=1, n_batches=None)
    for _ in range(1):
        for _ in logger.tqdm(range(10)):
            pass
    check.equal(logger.n_batches, 10)


def test_regex() -> None:
    """Test regex matching."""
    logger = Logger(
        n_epochs=10,
        n_batches=10,
        styles={".* loss": "red", "train loss": "blue", ".* acc": "green"},
    )
    for _ in range(10):
        for _ in logger.tqdm(range(10)):
            logger.log(
                {"val loss": 0.02, "train loss": 0.01, "train acc": 56, "val acc": 52},
                styles={"val.*": "yellow", "val acc": "blue"},
            )


def test_pause_resume() -> None:
    """Test pause and resume."""
    # pylint: disable=protected-access
    logger = Logger(
        n_epochs=1,
        n_batches=1,
    )
    logger.new_epoch()
    logger.new_batch()
    logger.log({"loss": 0.02})
    logger.pause()
    time.sleep(1.1)
    logger.resume()
    time_text = logger._build_time_info().plain
    time_parsed = time_text.split("global")[1].split("<")[0].strip()
    check.is_true(time_parsed.endswith("00"))
    check.is_true(logger.get_current_time() - logger._glob_time < 1)
    time.sleep(1.1)
    time_text = logger._build_time_info().plain
    time_parsed = time_text.split("global")[1].split("<")[0].strip()
    check.is_false(time_text.endswith("00"))
    check.is_true(logger.get_current_time() - logger._glob_time > 1)
