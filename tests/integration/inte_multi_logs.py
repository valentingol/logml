# Copyright (c) 2023 Valentin Goldite. All Rights Reserved.
"""Integration tests for multi logs on same step."""
from logml.logger import Logger


def main() -> None:
    """Integration test for multi logs on same step."""
    logger = Logger(1, 1)
    logger.new_epoch()
    logger.new_batch()
    logger.log({"loss1": 0.1}, styles="blue", message="ERROR")
    logger.log({"loss2": 0.2}, styles="red", message="Good")
    logger.log({"loss3": 0.3}, styles="yellow")
    logger.log({"loss4": 0.4}, styles="green")
    logger.log({"loss5": 0.5}, styles="blue")
    logger.log({"loss6": 0.6}, styles="red")
    logger.log({"loss7": 0.7}, styles="yellow")
    logger.log({"loss8": 0.8}, styles="green")
    logger.log({"loss9": 0.9}, styles="blue")
    logger.log({"loss10": 1.0}, styles="red")
    logger.log({"loss11": 1.1}, styles="yellow")
    logger.log({"loss12": 1.2}, styles="green")
    logger.log({"loss13": 1.3}, styles="blue")
    logger.log({"loss14": 1.4}, styles="red")


if __name__ == "__main__":
    main()
