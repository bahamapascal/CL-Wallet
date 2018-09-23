from iota import Iota
from messages import balance as balance_console_messages
from iota import Address


class Balance:
    """
    Class for managing account balance information.
    """

    def __init__(self, account):
        """
        Account class instance
        """

        self.account = account

    def find_balance(self, count):
        """
        Generates addresses and find balance against generated addresses.

        :param count:
          int: Number of addresses to generate.

        :return:
          None
        """

        """
        Quick hack for avoiding circular imports        
        """

        from address_manager import AddressManager
        from helpers import pretty_print, convert_units

        max_gap = 3
        margin = 4
        i = 0
        balance_found = False
        pretty_print(balance_console_messages['generating_addresses'], color='green')

        while i < count and margin > 0:
            info_message = balance_console_messages['checking_addresses']
            pretty_print(info_message.format(i + 1, count), color='green')

            address_manager = AddressManager(self.account)
            address_manager.generate(1)

            index_list = []

            for data in self.account.data['account_data']['address_data']:
                index = data['index']
                index_list.append(index)
            max_index = max(index_list)
            for data in self.account.data['account_data']['address_data']:
                index = data['index']
                balance = data['balance']
                if index == max_index and balance > 0:
                    balance_found = True
                    address = data['address']

                    balance_found_info_message = balance_console_messages['balance_found']
                    pretty_print(
                        balance_found_info_message.format(
                            index,
                            address,
                            convert_units(self.account.data['account_data']['settings']['units'], balance)
                        ),
                        color='green'
                    )
                    margin = max_gap
                    if count - i <= max_gap:
                        count += max_gap

                elif index == max_index and margin <= max_gap:
                    margin -= 1

            i += 1
        if not balance_found:
            pretty_print(balance_console_messages['no_address_with_balance'], color='red')

    def retrieve(self, address):
        """
        Finds balance for given address.

        :param address:
          str: Address.

        :return:
          int: Balance for address.
        """

        api = Iota(self.account.data['account_data']['settings']['host'])
        gna_result = api.get_balances([Address(address).address])
        balance = gna_result['balances']

        return balance[0]

    def get_balances(self, addresses):
        """
        Finds balances for given addresses.

        :param addresses:
          list: Addresses.

        :return:
          list: Balances.
        """

        api = Iota(self.account.data['account_data']['settings']['host'])
        gna_result = api.get_balances(addresses)

        return gna_result['balances']

    def write_fal_balance(self, f_index=0, l_index=0):
        """
        Writes updated account data to file.

        :param f_index:
          int: first index.

        :param l_index:
          int: last index.

        :return:
          None.
        """

        account_clone = self.account.data.copy()

        if f_index > 0 and l_index > 0:
            account_clone['account_data']['fal_balance']['f_index'] = f_index
            account_clone['account_data']['fal_balance']['l_index'] = l_index

        elif f_index > 0:
            account_clone['account_data']['fal_balance']['f_index'] = f_index
        elif l_index > 0:
            account_clone['account_data']['fal_balance']['l_index'] = l_index
        else:
            return  # TODO: Improve this

        self.account.update_data(account_clone)

    def update_fal_balance(self):
        """
        Updates account data with latest balance.

        :return:
          None.
        """

        index_with_value = []

        for data in self.account.data['account_data']['address_data']:
            if data['balance'] > 0:
                index = data['index']
                index_with_value.append(index)

        if len(index_with_value) > 0:
            f_index = min(index_with_value)
            l_index = max(index_with_value)

            self.write_fal_balance(f_index, l_index)

    def update_addresses_balance(self, start_index=0):
        """
        Updates balance for addresses.

        :param start_index:
          int: Start index.

        :return:
          None.
        """

        from helpers import pretty_print

        max_index = 0
        for data in self.account.data['account_data']['address_data']:
            index = data['index']
            if start_index <= index:
                address = str(data['address'])
                balance = self.retrieve(address)
                self.save_to_account_file(index, address, balance)

            if max_index < index:
                max_index = index

        if max_index < start_index:
            pretty_print(balance_console_messages['start_index_not_found'], color='red')

    def save_to_account_file(self, index, address, balance):
        """
        Saves updated address data to account file.

        :param index:
          int: Start index.

        :param address:
          str: Address.

        :param balance:
          int: Balance.

        :return:
          None.
        """

        from helpers import address_checksum, get_checksum, is_py2

        address = address_checksum(address) if is_py2 else address_checksum(address.encode())

        account_clone = self.account.data.copy()

        for p in account_clone['account_data']['address_data']:
            if p['address'] == address.decode():
                p['balance'] = balance

                self.account.update_data(account_clone)
                return

        checksum = get_checksum(address.decode(), self.account.seed)
        account_clone['account_data']['address_data'].append({
            'index': index,
            'address': address.decode(),
            'balance': balance,
            'checksum': checksum
        })

        self.account.update_data(account_clone)
