from helpers import fetch_user_input
from address_manager import AddressManager
from balance import Balance
from help import Help
from account_info import AccountInfo
from account_history import AccountHistory
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
        if option == 'help':
            return Help()
        elif option == 'settings':
            return Settings(self.account)
        elif option == 'account info':
            return AccountInfo(self.account, standard=True)
        elif option == 'full account info':
            return AccountInfo(self.account)
        elif option == 'find balance':
            return Balance(self.account)
        elif option == 'generate new address':
            return AddressManager(self.account)
        elif option == 'send transfer':
            return Transfer(self.account)
        elif option == 'full account history':
            return AccountHistory(self.account, full=True)
        elif option == 'account history':
            return AccountHistory(self.account)

        return self.invariant()

    def invariant(self):
        print "FAILED"