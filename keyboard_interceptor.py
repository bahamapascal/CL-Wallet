import signal
import sys


class KeyboardInterruptHandler:
    def __init__(self, callback):
        self.interrupt = False
        self.input = None
        self.callback = callback

        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, sig, frame):
        self.prompt()

    def prompt(self):
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
