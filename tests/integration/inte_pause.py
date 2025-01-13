"""Integration tests for pause/resume."""
import time

from logml.logger import Logger


def main() -> None:
    """Integration test for pause/resume."""
    n_epochs = 3
    n_batches = 8
    logger = Logger(
        n_epochs=n_epochs,
        n_batches=n_batches,
    )
    for epoch in range(3):
        logger.new_epoch()
        logger.resume()
        for _ in logger.tqdm(range(n_batches)):
            time.sleep(0.25)
            logger.log(message="The global time eta + current should remain the same.")
        if epoch < 2:
            logger.pause()
            time.sleep(0.5)
            for _ in range(n_batches):
                time.sleep(0.25)


if __name__ == '__main__':
    main()
