from helpers import pretty_print, intercept_keyboard_interrupts
from account import Account
import config
from manage import Manage
from messages import wallet as console_messages


def main(account):
    """
    Wrapper for Manage class

    :param account:
        dict: Account class instance.

    :return:
        None
    """

    # intercept keyboard interrupts for forcefully killing wallet
    # Would help us gracefully exiting the wallet upon user confirmation
    intercept_keyboard_interrupts(lambda: main(account))
    execute = 1

    while execute:
        Manage(account)


def init():
    """
    Initializes wallet.

    :return:
        None
    """

    pretty_print(console_messages['welcome'])
    initial_settings = config.settings
    account = Account(initial_settings)

    main(account)


if __name__ == '__main__':
    init()
