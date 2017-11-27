from helpers import pretty_print


class Balance:
    def __init__(self, account):
        self.account = account

    def find_balance(self, count):
        max_gap = 3
        margin = 4
        i = 0
        balance_found = False
        pretty_print(
            'Generating addresses'
            ' and checking for balance, please wait...\n',
        )

        while i < count and margin > 0:
            pretty_print(
                'Checking address '
                + str(i + 1) + ' in range of '
                + str(count),
                color='green'
            )
            self.generate_addresses(1)
            index_list = []
            for data in self.account.data.account_data.address_data:
                index = data['index']
                index_list.append(index)
            max_index = max(index_list)
            for data in self.account.data.account_data.address_data:
                index = data['index']
                balance = data['balance']
                if index == max_index and balance > 0:
                    balance_found = True
                    address = data['address']
                    pretty_print(
                        'Balance found! \n' +
                        '   Index: ' + str(index) + '\n' +
                        '   Address: ' + str(address) + '\n' +
                        '   Balance: ' + convert_units(balance) + '\n',
                        color='green'
                    )
                    margin = max_gap
                    if count - i <= max_gap:
                        count += max_gap

                elif index == max_index and margin <= max_gap:
                    margin -= 1

            i += 1
        if not balance_found:
            pretty_print('No address with balance found!', color='red')

    def generate_addresses(self, count):
        index_list = [-1]
        for data in self.account.data.account_data.address_data:
            index = data['index']
            index_list.append(index)

        if max(index_list) == -1:
            start_index = 0
        else:
            start_index = max(index_list) + 1

        as_encoded = seed if is_py2 else seed.encode('utf-8')
        generator = AddressGenerator(as_encoded)

        '''
        This is the actual function to generate the address.
        '''
        addresses = generator.get_addresses(start_index, count)
        i = 0

        while i < count:
            index = start_index + i
            address = addresses[i]

            versionised_address = str(address) if is_py2 else bytes(address)
            balance = address_balance(versionised_address) if is_py2 else address_balance(versionised_address)
            write_address_data(index, versionised_address, balance) if is_py2 else write_address_data(index,
                                                                                                      versionised_address.decode(),
                                                                                                      balance)
            i += 1

        update_fal_balance()
