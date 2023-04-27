"""Test logger.py."""

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
        digits={'train acc': 2},
        styles='yellow',
        average=['train loss', 'train acc'],
        bold_keys=True,
    )
    logger.start()
    for i in range(2):
        for epoch in range(n_epochs):
            logger.new_epoch()
            for batch in range(n_batches):
                logger.new_batch()
                styles = {'train loss': 'green', 'train acc': 'blue'}
                logger.log(
                    {'train loss': 1-int(100*epoch/n_epochs)/100,
                     'train acc': 100-int(100*batch/n_batches)/100,
                     'mse': 0.2,
                     },
                    message='This is...\nok?',
                    styles=styles,
                    average=['mse'],
                )
        if i == 0:
            logger.reset()
            logger.bold_keys = False
            logger.n_batches = None
    logger.log({'new loss': 0.3}, styles='red', digits=3, message='\n')

    with check.raises(ValueError):
        logger = Logger(2, 5)
        logger.log({'train loss': 1, 'train acc': 1})
    with check.raises(ValueError):
        logger = Logger(2, 5)
        logger.new_epoch()
        logger.log({'train loss': 1, 'train acc': 1})
    with check.raises(ValueError):
        logger = Logger(2, 5)
        logger.new_batch()
        logger.log({'train loss': 1, 'train acc': 1})
