"""Integration tests for Logger."""

import time

from logml.logger import Logger


def main() -> None:
    """Integration test for Logger."""
    n_epochs = 3
    n_batches = 10
    logger = Logger(
        n_epochs=n_epochs,
        n_batches=n_batches,
        log_interval=2,
        sizes={"train acc": 2},
        styles="yellow",
        average=["train loss"],
        bold_keys=True,
    )
    logger.start()
    for i in range(2):
        for epoch in range(n_epochs):
            logger.new_epoch()
            for batch in range(n_batches):
                logger.new_batch()
                time.sleep(0.015)
                styles = {"train loss": "green", "train acc": "blue"}
                logger.log(
                    {
                        "train loss": 1 - epoch / n_epochs,
                        "train acc": 100 * batch / n_batches,
                        "loss name": 'mse',
                        "best run": True,
                    },
                    message="This is...\nok?",
                    styles=styles,
                    average=["mse"],
                )
        if i == 0:
            logger.reset()
            logger.bold_keys = False
            logger.n_batches = None
    logger.log(
        {f"new loss{i}": 0.3 for i in range(1, 20)},
        styles="red",
        sizes=3,
        message="\n",
    )
    print('tqdm:')
    logger = Logger(
        n_epochs=2,
        n_batches=10,
    )
    for _ in range(2):
        for _ in logger.tqdm(range(10)):
            logger.log({'loss': 0.02})
    print('regex:')
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
                    "val acc": 52
                },
                styles={"val.*": "yellow", "val acc": "orange3"}
            )
    print("Should be red, blue, green, yellow, orange")


if __name__ == "__main__":
    main()
