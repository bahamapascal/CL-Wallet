from helpers import fetch_user_input
from address_manager import AddressManager
from balance import Balance
from help import Help
from account_info import AccountInfo
from account_history import AccountHistory
from settings import Settings
from transfer import Transfer
from messages import manage as console_messages
from helpers import pretty_print


class Manage:
    def __init__(self, account):
        self.account = account
        self.input = None

        self.initialize()

    def initialize(self):
        self.input = fetch_user_input(console_messages['help_info'])

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
        pretty_print(console_messages['invariant'])