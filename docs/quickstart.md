# Quick start

## Minimal usage

Integrate the LogML logger in your training loops! For instance for 4 epochs,
20 batches per epoch and a log interval of 2 batches:

```python
from logml import Logger

logger = Logger(
    n_epochs=4,
    n_batches=20,
    log_interval=2,
)
for _ in range(4):
    logger.start_epoch()  # Indicate the start of a new epoch
    for _ in range(20):
        logger.start_batch()  # Indicate the start of a new batch
        logger.log({'loss': 0.54321256, 'accuracy': 0.85244777})
```

Yields:

```script
Epoch 1/4, batch 20/20
[================================================][100%]
[global 00:00:02 > 00:00:06 | epoch 00:00:02 > 00:00:00]
loss: 0.5432 | accuracy: 0.8524 |

Epoch 2/4, batch 8/20
[=================>                              ][40%]
[global 00:00:03 > 00:00:05 | epoch 00:00:01 > 00:00:01]
loss: 0.5432 | accuracy: 0.8524 |
```

## Advanced usage

Now you can customize the logger with your own styles and colors. You can set the default configuration at the initialization of the logger and then you can override it during log. You can also log the averaged value over the epoch. For instance:

```python
logger = Logger(
    n_epochs=4,
    n_batches=20,
    styles='yellow',
    sizes={'accuracy': 2},
    average=['loss'],  # loss will be averaged over the current epoch
    bold_keys=True,
    show_time=False,  # Remove the time bar
)
for _ in range(4):
    logger.start_epoch()
    for _ in range(20):
        logger.start_batch()
        # Overwrite the default style for "loss" and add a message
        logger.log(
            {'loss': 0.54321256, 'accuracy': 85.244777},
            styles={'loss': 'italic red'},
            message="Training is going well?\nYes!",
        )
```

Yields:

```script
Epoch 1/4, batch 20/20
[================================================][100%]
loss: 0.5432 | accuracy: 85 |

Epoch 2/4, batch 7/20
[=================>                              ][35%]
[global 00:00:03 > 00:00:05 | epoch 00:00:01 > 00:00:01]
loss: 0.5432 | accuracy: 85 |
Training is going well?
Yes!
```

But with this style:

<span style="color:red">***loss*** *: 0.5432*</span> |
<span style="color:yellow">**accuracy**: 85</span> |
