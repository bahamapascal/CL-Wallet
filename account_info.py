from iota import Iota, ProposedTransaction, Address,\
    TryteString, Tag, Transaction
from helpers import is_py2, pretty_print, address_checksum, get_checksum, yes_no_user_input, numbers_user_input, verify_checksum, \
    convert_units
from messages import account_info as account_info_console_messages
from balance import Balance
from address_manager import AddressManager


class AccountInfo:
    def __init__(self, account, standard=False):
        self.account = account
        self.standard_account_info = standard

        if self.standard_account_info:
            self.get_standard_account_info()
        else:
            self.get_full_account_info()

    def get_full_account_info(self):
        pass

    def update_addresses_balance(self, start_index=0):
        max_index = 0
        for data in self.account.data['account_data']['address_data']:
            index = data['index']
            if start_index <= index:
                address_manager = AddressManager(self.account)
                balance_manager = Balance(self.account)

                address = str(data['address'])
                balance = balance_manager.retrieve(address)
                address_manager.save_to_account_file(index, address, balance)

            if max_index < index:
                max_index = index

        if max_index < start_index:
            pretty_print(account_info_console_messages['start_index_not_found'], color='red')

    def update_fal_balance(self):
        index_with_value = []

        for data in self.account.data['account_data']['address_data']:
            if data['balance'] > 0:
                index = data['index']
                index_with_value.append(index)

        if len(index_with_value) > 0:
            f_index = min(index_with_value)
            l_index = max(index_with_value)

            balance_manager = Balance(self.account)

            balance_manager.write_fal_balance(f_index, l_index)

    def get_standard_account_info(self):
        address_count = len(self.account.data['account_data']['address_data'])
        self.update_addresses_balance(self.account.data['account_data']['fal_balance']['f_index'])
        self.update_fal_balance()

        if address_count < 1:
            pretty_print(account_info_console_messages['scan_balance_prompt'])
            yes = yes_no_user_input()

            if yes:
                pretty_print(account_info_console_messages['address_generation_prompt'])
                prompt = account_info_console_messages['maximum_addresses_prompt']
                addresses_to_check = numbers_user_input(prompt)

                if addresses_to_check > 0:
                    balance_blueprint = Balance(self.account)
                    balance_blueprint.find_balance(addresses_to_check)

                    self.get_standard_account_info()

                elif addresses_to_check == 0:
                    pretty_print(account_info_console_messages['no_addresses_entered'], color='green')
            elif not yes:
                pretty_print(account_info_console_messages['generate_deposit_address'])
                address_manager = AddressManager(self.account)

                address_manager.generate(1)

                self.get_standard_account_info()

        elif address_count > 0:
            all_address_data = ''
            total_balance = 0

            account_clone = self.account.data.copy()

            for p in account_clone['account_data']['address_data']:
                balance = p['balance']
                address = p['address']
                checksum = p['checksum']
                integrity = verify_checksum(checksum, address, self.account.seed)

                if balance > 0 and integrity:
                    total_balance += balance
                    data = account_info_console_messages['address_balance_info'.format(
                        p['index'],
                        address,
                        convert_units(self.account.data['account_data']['settings']['units'], balance)
                    )]

                    all_address_data += data

                elif not integrity:
                    total_balance += balance
                    data = account_info_console_messages['invalid_checksum'.format(p['index'])]
                    all_address_data += data

            address_manager = AddressManager(self.account)
            if total_balance > 0:
                pretty_print(all_address_data)
                pretty_print(account_info_console_messages['deposit_address'] + str(address_manager.get_deposit_address()), color='blue')
                pretty_print(account_info_console_messages['total_balance'] +
                             convert_units(self.account.data['account_data']['settings']['units'], total_balance))

            else:
                pretty_print('No addresses with balance!', color='red')
                pretty_print('\n' + 'Deposit address: ' + str(address_manager.get_deposit_address()), color='blue')
