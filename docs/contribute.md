# How to contribute

For **development**, install the package dynamically and dev requirements with:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

Everyone can contribute to LogML, and we value everyone’s contributions. Please see our
[contributing guidelines](https://github.com/valentingol/logml/blob/main/CONTRIBUTING.md)
for more information 🤗

## Todo list

To do:

Done:

- [x] Allow multiple logs on the same batch
- [x] Finalize tests for 1.0.0 major release
- [x] Add docs sections: comparison with tqdm and how to use mean_vals
  (with exp tracker)
- [x] Use regex for `styles`, `sizes` and `average` keys
- [x] Be compatible with notebooks
- [x] Get back the cursor when interrupting the training
- [x] `logger.tqdm()` feature (used like `tqdm.tqdm`)
- [x] Doc with Sphinx
- [x] Be compatible with Windows and Macs
- [x] Manage a validation loop (then multiple loggers)
- [x] Add color customization for message, epoch/batch number and time
