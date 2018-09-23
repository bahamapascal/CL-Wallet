from terminaltables import SingleTable
from helpers import pretty_print, yes_no_user_input, numbers_user_input, verify_checksum, \
    convert_units
from messages import account_info as account_info_console_messages
from balance import Balance
from address_manager import AddressManager


class AccountInfo:
    """
    Contains account (Addresses) information.
    """

    def __init__(self, account, standard=False):
        """
        Account class instance
        """

        self.account = account

        """
        Decides whether to display full/partial account info.
        """
        self.standard_account_info = standard

        if self.standard_account_info:
            self.get_standard_account_info()
        else:
            self.get_full_account_info()

    def render_full_account_information(self, address_data):
        """
        Displays full address information on console.

        :param address_data:
          list: Address related data.

        :return:
          None
        """

        table_title = 'Full Account Information'
        table_data = [(
            ('Index', 'Address', 'Balance', 'Integrity')
        )]

        for d in address_data:
            address = d['address']
            checksum = d['checksum']
            balance = int(d['balance'])
            index = d['index']

            has_valid_checksum = verify_checksum(checksum, address, self.account.seed)

            table_data.insert(
                len(table_data),
                (
                    index,
                    address,
                    balance,
                    'Valid Checksum' if has_valid_checksum else 'Invalid Checksum'
                )
            )

        table_instance = SingleTable(table_data, table_title)
        table_instance.inner_row_border = True

        pretty_print(table_instance.table, color='blue')

    def get_full_account_info(self):
        """
        Gets full account (addresses) information.

        :return:
          None
        """

        balance_manager = Balance(self.account)

        balance_manager.update_addresses_balance(self.account.data['account_data']['fal_balance']['f_index'])
        balance_manager.update_fal_balance()

        if len(self.account.data['account_data']['address_data']) > 0:
            self.render_full_account_information(self.account.data['account_data']['address_data'])

            first_index_with_balance_info_message = account_info_console_messages['first_index_with_balance']
            last_index_with_balance_info_message = account_info_console_messages['last_index_with_balance']
            first_index = self.account.data['account_data']['fal_balance']['f_index']
            last_index = self.account.data['account_data']['fal_balance']['l_index']

            pretty_print(first_index_with_balance_info_message.format(str(first_index)))
            pretty_print(last_index_with_balance_info_message.format(str(last_index)))
        else:
            pretty_print(account_info_console_messages['no_data'], color='red')

    def get_standard_account_info(self):
        """
        Gets basic account information

        :return:
            None
        """

        # Initialize address manager
        address_manager = AddressManager(self.account)

        # Check if account has any address information stored locally
        has_addresses = len(address_manager.get_addresses()) > 0

        # balance_manager.update_addresses_balance(self.account.data['account_data']['fal_balance']['f_index'])
        # balance_manager.update_fal_balance()

        # If has no addresses in the history, then prompt user to generate addresses
        if not has_addresses:
            pretty_print(account_info_console_messages['scan_balance_prompt'])
            yes = yes_no_user_input()

            if yes:
                pretty_print(account_info_console_messages['address_generation_prompt'])
                prompt = account_info_console_messages['maximum_addresses_prompt']

                addresses_to_generate = numbers_user_input(prompt)

                if addresses_to_generate > 0:
                    # Generate addresses, find latest balances against those addresses and save to file
                    address_manager.generate_addresses_with_data(addresses_to_generate, persist=True)

                    self.get_standard_account_info()

                elif addresses_to_generate == 0:
                    pretty_print(account_info_console_messages['no_addresses_entered'], color='green')
            elif not yes:
                pretty_print(account_info_console_messages['generate_deposit_address'])

                address_manager.generate(1)

                self.get_standard_account_info()
        else:
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
                    data = account_info_console_messages['address_balance_info'].format(
                        p['index'],
                        address,
                        convert_units(self.account.data['account_data']['settings']['units'], balance)
                    )

                    all_address_data += data

                elif not integrity:
                    total_balance += balance
                    data = account_info_console_messages['invalid_checksum'.format(p['index'])]
                    all_address_data += data

            address_manager = AddressManager(self.account)
            if total_balance > 0:
                pretty_print(all_address_data)
                pretty_print(
                    account_info_console_messages['deposit_address'] + str(address_manager.get_deposit_address()),
                    color='blue')
                pretty_print(account_info_console_messages['total_balance'] +
                             convert_units(self.account.data['account_data']['settings']['units'], total_balance))

            else:
                pretty_print('No addresses with balance!', color='red')
                pretty_print('\n' + 'Deposit address: ' + str(address_manager.get_deposit_address()), color='blue')

