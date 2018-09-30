import signal
import sys


class KeyboardInterruptHandler:
    """
    Class for managing keyboard interrupts while the wallet is running.
    """
    def __init__(self, callback):
        """
        Decides if a keyboard interrupt is received.
        """

        self.interrupt = False

        """
        User confirmation input to check if he/she really wants to close the wallet.
        """
        self.input = None

        """
        Function that gets called if a user accidentally pressed (ctrl + c) to close wallet.
        """
        self.callback = callback

        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, sig, frame):
        self.prompt()

    def prompt(self):
        """
        Asks for user confirmation if he/she wants to close wallet.

        :return:
          None
        """

        from helpers import confirms, fetch_user_input, pretty_print

        pretty_print('\nWe hate to see you go. Are you sure you want to quit?')
        while not self.interrupt:
            self.input = fetch_user_input('Press [y] to quit or any other key to [cancel].')

            if confirms(self.input):
                self.interrupt = True
                pretty_print('\nSee you soon!')
                sys.exit(0)
            else:
                self.callback()
