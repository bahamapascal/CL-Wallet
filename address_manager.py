from iota.crypto.addresses import AddressGenerator
from helpers import pretty_print, is_py2, verify_checksum
from messages import address_manager as address_manager_console_messages
from balance import Balance


class AddressManager:
    def __init__(self, account):
        self.account = account

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