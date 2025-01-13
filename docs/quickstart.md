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

## Pause and resume

You can also pause and resume the logger internal time with `logger.pause()` and
`logger.resume()`. You can check the internal time with `logger.get_current_time()`.
Note that the resume method continues the time from **the last pause**.
it means that if you pause the training logger at 10 seconds, then resume it
at 20 seconds, the logger will display 10 seconds of training time. The global and
the epoch time will be updated accordingly. You can also find examples in
the documentation.

## Save the logs

In Linux you can use `tee` to save the logs in a file and display them in the console.
However you need to use `unbuffer` to keep the style:

```bash
unbuffer python main.py --color=auto | tee output.log
```

See
[here](https://superuser.com/questions/352697/preserve-colors-while-piping-to-tee)
for details.

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
)
val_logger = Logger(
    n_epochs=2,
    n_batches=10,
    name='Validation',
    name_style='cyan',
    styles='blue',
    bold_keys=True,
    show_time=False,  # Remove the time bar
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

Further features are described in the *Features* section.
