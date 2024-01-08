# Copyright (c) 2023 Valentin Goldite. All Rights Reserved.
"""Integration tests for Logger.tqdm."""
from logml.logger import Logger


def main() -> None:
    """Integration test for Logger.tqdm."""
    logger = Logger(
        n_epochs=2,
        n_batches=10,
    )
    for _ in range(2):
        logger.new_epoch()  # Not necessary
        for _ in logger.tqdm(range(10)):
            logger.new_batch()  # Not necessary
            logger.log({"loss": 0.02})


if __name__ == "__main__":
    main()
