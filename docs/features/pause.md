# Pause and resume

You can also pause and resume the logger internal time with `logger.pause()` and
`logger.resume()`. You can check the internal time with `logger.get_current_time()`.
Note that the resume method continues the time from **the last pause**.
it means that if you pause the training logger at 10 seconds, then resume it
at 20 seconds, the logger will display 10 seconds of training time. The global and
the epoch time will be updated accordingly. You can also find examples in
the documentation.

Example:

```python
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
            logger.log(
                message="The global time (eta + current) remains the same (6 sec)."
            )
        logger.pause()  # -> Pause during evaluation times
        time.sleep(0.5)
        for _ in range(n_batches):
            time.sleep(0.25)
```

Here the logger is paused during the evaluation times.
The global time (eta + current) remains the same (6 sec) after the pause:

![Alt Text](../_static/pause.gif)
