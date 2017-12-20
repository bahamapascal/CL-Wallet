from iota.crypto.addresses import AddressGenerator
from helpers import pretty_print, is_py2, address_checksum, get_checksum, verify_checksum
from messages import address_manager as address_manager_console_messages
from balance import Balance


class AddressManager:
    def __init__(self, account):
        self.account = account

    def save_to_account_file(self, index, address, balance):
        # Should not mutate here (address)
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

            self.save_to_account_file(index, versionised_address, balance) if is_py2 else \
                self.save_to_account_file(index,
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