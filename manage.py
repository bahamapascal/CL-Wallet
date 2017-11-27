from helpers import fetch_user_input
from address_manager import AddressManager
from balance import Balance
from help import Help
from account_info import AccountInfo
from settings import Settings
from transfer import Transfer


class Manage:
    def __init__(self, account):
        self.account = account
        self.input = None

        self.options = {
            'settings': Settings,
            'help': Help,
            'account info': AccountInfo,
            'full account info': AccountInfo,
            'find balance': Balance,
            'generate new address': AddressManager,
            'send transfer': Transfer,
            'full account history': AccountInfo,
            'account history': AccountInfo,
            'replay': AccountInfo,
            'exit': AccountInfo,
        }

        self.initialize()

    def initialize(self):
        self.input = fetch_user_input('\n \nPlease enter a command.'
                                   ' Type \'HELP\' to see '
                                   'all avaliable commands:  ')

        return self.manage(self.input)

    def manage(self, option):
        without_args = [
            'help'
        ]

        with_args = [
            'settings',
            'account info',
            'full account info',
            'find balance',
            'generate new address',
            'send transfer',
            'full account history',
            'account history',
            'replay',
            'exit'
        ]

        if option in without_args and option not in with_args:
            return self.options[option]()
        elif option in with_args and option not in without_args:
            return self.options[option](self.account)

        return self.validate()

    def validate(self):
        print "FAILED"