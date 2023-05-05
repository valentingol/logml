echo "*********** Integration tests ***********"
echo "*** logger ***"
python tests/integration/inte_logger.py
echo "*** regex ***"
python tests/integration/inte_regex.py
echo "*** tqdm ***"
python tests/integration/inte_tqdm.py
echo "*** 2 loggers ***"
python tests/integration/inte_two_loggers.py
