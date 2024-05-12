import logging

from colorama import Fore, Style


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(levelname)s] %(message)s')

    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


def write(text: str, role: str = "user", agent: str = "X") -> None:
    if role == "assistant":
        prGreen(f"Agent {agent}: {text}")
    else:
        print(f"User: {text}")


def prGreen(skk: str) -> None:
    print(f"{Fore.GREEN}{Style.BRIGHT}{skk}{Style.RESET_ALL}")
