# Use LoggerML with experiment tracker (like Weights and Biases)

LoggerML was has been designed to integrate with tracking libraries like Weights and
Biases. The log method takes as input a dictionary of values in the same way as
`wandb.log` for instance. In addition, the logger stores the averages of the numerical
values so that they can be easily logged as well with an experiment tracker.

With Weights and Biases you can do this for instance:

```python
# NOTE: 'mean.*' means all keys starting with 'mean'
logger = Logger(n_epochs=4, n_batches=20, average=['mean.*'])
for _ in range(4):
    for _ in logger.tqdm(range(20)):

        # <Train here>
        loss = ...
        accuracy = ...

        values = {
            'loss': loss,
            'accuracy': accuracy,
            # 'mean loss' and 'mean accuracy' will be averaged
            # over the epoch before logging
            'mean loss': loss,
            'mean accuracy': accuracy,
        }
        # Log 'loss' and 'accuracy' of each individual batch and 'mean loss'
        # and 'mean accuracy' averaged over the epoch
        logger.log(values)
        # Do the same with wandb using `get_vals` method
        wandb.log(logger.get_vals(average=['mean.*']), step=logger.step)
```

The values passed to `logger.logs` (not averaged!) are also accessible via `logger.vals`
and the corresponding averages via `logger.mean_vals`.

Note that `logger.step` count the number of batches since the beginning of the
experiment. It is exactly the same parameter as `wandb.log`'s `step` parameter.
