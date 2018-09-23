from operator import attrgetter
from iota.crypto.addresses import AddressGenerator
from helpers import pretty_print, is_py2, verify_checksum, address_checksum, get_checksum
from messages import address_manager as address_manager_console_messages
from balance import Balance


class AddressManager:
    def __init__(self, account):
        self.account = account

    def generate_addresses_with_data(self, count, persist=False):
        """
        Generate addresses and (optionally) store to file

        :param count:
            Number of addresses to generate

        :param persist:
            Decides if addresses should be saved to file

        :return:
            List of new generated addresses
        """

        # Initialize address generator
        generator = AddressGenerator(self.account.seed if is_py2 else self.account.seed.encode('utf-8'))

        # Get locally stored addresses
        addresses_with_data = self.get_addresses_with_data()

        # Initialize balance manager
        balance_manager = Balance(self.account)

        # Check if there are locally stored addresses
        has_no_addresses = len(addresses_with_data) == 0

        # When there are no locally stored addresses, start with index 0
        # Otherwise start from latest address index + 1
        start_index = 0 if has_no_addresses else max(addresses_with_data, key=attrgetter('index')).attr + 1

        new_addresses = generator.get_addresses(start_index, count)

        # Find latest balances on addresses
        balances = balance_manager.get_balances(new_addresses)

        # Create a list of address indexes
        indexes = [index for index in range(start_index, count)]

        addresses_with_data = self.format_addresses(new_addresses, indexes, balances)

        if persist:
            account = self.account.data.copy()

            # Update address_data in file
            account['account_data']['address_data'] = account['account_data']['address_data'] + addresses_with_data

            # Write to account file
            self.account.update_data(account)

        return addresses_with_data

    def format_addresses(self, addresses, indexes, balances):
        """

        :param addresses:
            List of addresses

        :param indexes:
            List of address indexes

        :param balances:
            List of address balances

        :return:
            List of formatted address data
        """
        addresses_with_data = []

        for address_list_index, item in enumerate(addresses):
            address = address_checksum(item) if is_py2 else address_checksum(item.encode())

            addresses_with_data.append({
                'index': indexes[address_list_index],
                'address': address.decode(),
                'balance': balances[address_list_index],
                'checksum': get_checksum(address.decode(), self.account.seed)
            })

        return addresses_with_data

    def generate(self, count):
        index_list = [-1]
        for data in self.account.data['account_data']['address_data']:
            index = data['index']
            index_list.append(index)

        if max(index_list) == -1:
            start_index = 0
        else:
            start_index = max(index_list) + 1

        as_encoded = self.account.seed if is_py2 else self.account.seed.encode('utf-8')
        generator = AddressGenerator(as_encoded)

        '''
        This is the actual function to generate the address.
        '''
        addresses = generator.get_addresses(start_index, count)
        i = 0

        balance_blueprint = Balance(self.account)
        while i < count:
            index = start_index + i
            address = addresses[i]

            versionised_address = str(address) if is_py2 else bytes(address)
            balance = balance_blueprint.retrieve(versionised_address) if is_py2 else balance_blueprint.retrieve(versionised_address)

            balance_blueprint.save_to_account_file(index, versionised_address, balance) if is_py2 else \
                balance_blueprint.save_to_account_file(index,
                                          versionised_address.decode(),
                                          balance
                            )
            i += 1

        balance_blueprint.write_fal_balance()

    def get_deposit_address(self):
        try:
            l_index = self.account.data['account_data']['fal_balance']['l_index']
            if l_index == 0:
                deposit_address = self.account.data['account_data']['address_data'][0]['address']

                return deposit_address

            for p in self.account.data['account_data']['address_data']:
                address = p['address']
                checksum = p['checksum']
                integrity = verify_checksum(checksum, address, self.account.seed)

                if p['index'] > l_index and integrity:
                    deposit_address = p['address']
                    return deposit_address

                elif not integrity:
                    return address_manager_console_messages['invalid_checksum']

            pretty_print(address_manager_console_messages['generating_address'], color='blue')
            self.generate(1)

            for p in self.account.data['account_data']['address_data']:
                address = p['address']
                checksum = p['checksum']
                integrity = verify_checksum(checksum, address, self.account.seed)
                if p['index'] > l_index and integrity:
                    deposit_address = p['address']
                    return deposit_address
        except ValueError as e:
            pretty_print(address_manager_console_messages['deposit_address_exception'])

    def get_addresses_with_data(self):
        """
        Gets list of addresses with related data

        :return:
            List of addresses with data (
                index,
                checksum,
                balance,
                address
            )
        """
        return self.account.data['account_data']['address_data']

    def get_addresses(self):
        """
        Gets list of all addresses

        :return:
            List of all addresses [ATE, YTK, DEI, ...]
        """
        addresses_with_data = self.get_addresses_with_data()

        return [address['address'] for address in addresses_with_data]
