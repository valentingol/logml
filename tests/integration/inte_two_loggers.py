"""Integration tests for 2 loggers."""

import time

from logml.logger import Logger


def main() -> None:
    """Integration test for Logger."""
    n_epochs = 2
    n_batches_train = 20
    n_batches_val = 5
    train_logger = Logger(
        n_epochs,
        n_batches_train,
        name="Training",
        name_style="bold dark_orange",
        styles="red",
    )
    val_logger = Logger(
        n_epochs,
        n_batches_val,
        name="Validation",
        name_style="bold cyan",
        styles="blue",
    )
    for _ in range(n_epochs):
        train_logger.new_epoch()
        for _ in range(n_batches_train):
            train_logger.new_batch()
            time.sleep(0.03)
            train_logger.log({"train loss": 0.1})
        val_logger.new_epoch()
        for _ in range(n_batches_val):
            val_logger.new_batch()
            time.sleep(0.06)
            val_logger.log({"val loss": 0.1})


if __name__ == "__main__":
    main()
