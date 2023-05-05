# Quick start

## Minimal usage

Integrate the LogML logger in your training loops! For instance for 4 epochs
and 20 batches per epoch:

```python
import time

from logml import Logger

logger = Logger(n_epochs=4, n_batches=20)

for _ in range(4):
    for _ in logger.tqdm(range(20)):
        time.sleep(0.1)  # Simulate a training step
        # Log whatever you want (int, float, str, bool):
        logger.log({
            'loss': 0.54321256,
            'accuracy': 0.85244777,
            'loss name': 'MSE',
            'improve baseline': True,
        })
```

Yields:

![Alt Text](_static/base.gif)

Note that the expected remaining time of the overall train is displayed as well as
the one for the epoch. The logger also provides also the possibility to average the
logged values over an epoch or a full training.

## Advanced usage

Now you can add a validation logger, customize the logger with your own styles
and colors, compute the average of some values over batch, add a dynamic
message at each batch, update the value only every some batches and more!

At initialization you can set default configuration for the logger that will be
eventually overwritten by the configuration passed to the `log` method.

An example with more features:

```python
train_logger = Logger(
    n_epochs=2,
    n_batches=20,
    log_interval=2,
    name='Training',
    name_style='dark_orange',
    styles='yellow',  # Default style for all values
    sizes={'accuracy': 4},  # only 4 characters for 'accuracy'
    average=['loss'],  # 'loss' will be averaged over the current epoch
    bold_keys=True,  # Bold the keys
    show_time=False,  # Remove the time bar
)
val_logger = Logger(
    n_epochs=2,
    n_batches=10,
    name='Validation',
    name_style='cyan',
    styles='blue',
    bold_keys=True,
    show_time=False,
)
for _ in range(2):
    train_logger.new_epoch()  # Manually declare a new epoch
    for _ in range(20):
        train_logger.new_batch()  # Manually declare a new batch
        time.sleep(0.1)
        # Overwrite the default style for "loss" and add a message
        train_logger.log(
            {'loss': 0.54321256, 'accuracy': 85.244777},
            styles={'loss': 'italic red'},
            message="Training is going well?\nYes!",
        )
    val_logger.new_epoch()
    for _ in range(10):
        val_logger.new_batch()
        time.sleep(0.1)
        val_logger.log({'val loss': 0.65422135, 'val accuracy': 81.2658775})
    val_logger.detach()  # End the live display to print something else after
```

Yields:

![Alt Text](_static/advanced.gif)
