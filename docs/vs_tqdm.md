# Why not use tqdm.tqdm?

The [tqdm module](https://github.com/tqdm/tqdm) is a famous library widely used to
create dynamic progress bars. LoggerML's philosophy is to create a similar behavior
but **oriented in the practice of machine learning**.  Thus, LoggerML assumes that our
python code is organized into epochs and runs through batches of a dataset with
values to log. In this context, it gives additional information such as
the time remaining until the training is completed.

It also has a much nicer and customizable logging system: the values are organized
in tables below the progress bar and use the `rich` api to style the output.

Finally, the LoggerML logger compute the mean of **all** numerical values average
over epoch (by default) or the overall training. It is particularly interesting as we
often need to compute these means for meaningful logging.
