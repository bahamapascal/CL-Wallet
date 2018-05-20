import sys
from helpers import fetch_user_input
from address_manager import AddressManager
from help import Help
from account_info import AccountInfo
from account_history import AccountHistory
from settings import Settings
from transfer import Transfer
from messages import manage as console_messages
from helpers import pretty_print, find_balance, handle_replay, handle_promotion


class Manage:
    def __init__(self, account):
        self.account = account
        self.input = None

        self.initialize()

    def initialize(self):
        self.input = fetch_user_input(console_messages['help_info'])

        return self.manage(self.input)

    def manage(self, option):
        if 'replay' in option:
            account_clone = self.account.data.copy()

            min_weight_magnitude = account_clone['account_data']['settings']['min_weight_magnitude']
            node = account_clone['account_data']['settings']['host']
            transfers_data = account_clone['account_data']['transfers_data']

            return handle_replay(
                node,
                self.account.seed,
                option,
                transfers_data,
                min_weight_magnitude=min_weight_magnitude
            )
        elif 'promote' in option:
            account_clone = self.account.data.copy()

            min_weight_magnitude = account_clone['account_data']['settings']['min_weight_magnitude']
            node = account_clone['account_data']['settings']['host']
            transfers_data = account_clone['account_data']['transfers_data']

            return handle_promotion(
                node,
                option,
                transfers_data,
                min_weight_magnitude=min_weight_magnitude
            )
        elif option == 'help':
            return Help()
        elif option == 'settings':
            return Settings(self.account)
        elif option == 'account info':
            return AccountInfo(self.account, standard=True)
        elif option == 'full account info':
            return AccountInfo(self.account)
        elif option == 'find balance':
            return find_balance(self.account)
        elif option == 'generate new address':
            pretty_print(console_messages['generate_new_address'])
            manager = AddressManager(self.account)
            return manager.generate(1)
        elif option == 'send transfer':
            return Transfer(self.account)
        elif option == 'full account history':
            return AccountHistory(self.account, full=True)
        elif option == 'account history':
            return AccountHistory(self.account)
        elif option == 'logout' or option == 'exit':
            return sys.exit(0)  # Dirty hack because too sleepy. Should be smooth exit.

        return self.invariant()

    def invariant(self):
        pretty_print(console_messages['invariant'])
