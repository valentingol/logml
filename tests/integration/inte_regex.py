# Copyright (c) 2023 Valentin Goldite. All Rights Reserved.
"""Integration tests for Logger regex."""
from logml.logger import Logger


def main() -> None:
    """Integration test for Logger regex."""
    logger = Logger(
        n_epochs=1,
        n_batches=1,
        styles={".* loss": "red", "train loss": "blue", ".* acc": "green"},
    )
    for _ in range(1):
        for _ in logger.tqdm(range(1)):
            logger.log(
                {
                    "interm loss": 0.04,
                    "train loss": 0.01,
                    "train acc": 56,
                    "val loss": 0.02,
                    "val acc": 52,
                },
                styles={"val.*": "yellow", "val acc": "orange3"},
            )
    print("Should be red, blue, green, yellow and orange.")


if __name__ == "__main__":
    main()
