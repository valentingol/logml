echo "*********** Integration tests ***********"
echo "*** logger ***"
python tests/integration/inte_logger.py
echo ""
echo "*** regex ***"
python tests/integration/inte_regex.py
echo ""
echo "*** tqdm ***"
python tests/integration/inte_tqdm.py
echo ""
echo "*** 2 loggers ***"
python tests/integration/inte_two_loggers.py
echo ""
echo "*** multi logs ***"
python tests/integration/inte_multi_logs.py
echo ""
echo "*** pause/resume ***"
python tests/integration/inte_pause.py
