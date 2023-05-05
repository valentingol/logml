# How to use LoggerML with experiment tracker (like Weights and Biases)?

LoggerML was has been designed to integrate with tracking libraries like Weights and
Biases. The log method takes as input a dictionary of values in the same way as
`wandb.log` for instance. In addition, the logger stores the averages of the numerical
values so that they can be easily logged as well with an experiment tracker.

With Weights and Biases you can do this for instance:

```python
logger = Logger(n_epochs=4, n_batches=20)
for _ in range(4):
    for _ in logger.tqdm(range(20)):

        # <Train here>
        loss = ...
        accuracy = ...

        values = {
            'loss': loss,
            'accuracy': accuracy,
        }
        logger.log(values)
        wandb.log(values, step=logger.step)  # Log individual values of each batch
    wandb.log({
        'mean loss':logger.mean_values['loss']
        'mean accuracy':logger.mean_values['accuracy']
    })  # Log loss and accuracy averaged over epoch
```
