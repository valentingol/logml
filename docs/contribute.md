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

Priority:

- [ ] Doc with Sphinx
- [ ] Get back the cursor when interrupting the training

Secondary:

- [ ] Be compatible with notebooks
- [ ] Explain how to use a tracker log (wandb for instance) with LogML
- [ ] Use regex for `styles`, `sizes` and `average` keys

Done:

- [x] Be compatible with Windows and Macs
- [x] Manage a validation loop (then multiple loggers)
- [ ] ~~Enable not using `new_epoch/log()` if log config is minimal~~
- [x] Add color customization for message, epoch/batch number and time
