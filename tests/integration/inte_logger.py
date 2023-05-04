"""Integration tests for Logger."""

import time

from logml.logger import Logger


def main() -> None:
    """Integration test for Logger."""
    n_epochs = 5
    n_batches = 10
    logger = Logger(
        n_epochs=n_epochs,
        n_batches=n_batches,
        log_interval=2,
        digits={"train acc": 2},
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
                time.sleep(0.02)
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
        digits=3,
        message="\n",
    )


if __name__ == "__main__":
    main()
