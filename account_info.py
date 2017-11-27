from iota import Iota, ProposedTransaction, Address,\
    TryteString, Tag, Transaction
from helpers import is_py2, pretty_print, address_checksum, get_checksum


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

    def write_address_data(self, index, address, balance):
        addr = address_checksum(address) if is_py2 else address_checksum(address.encode())
        account_clone = self.account.data.copy()
        address_data = account_clone.account_data.address_data

        for p in address_data:
            if p['address'] == addr.decode():
                p['balance'] = balance
                self.account.update_data(account_clone)
                return

        checksum = get_checksum(addr.decode())

        address_data.append({
            'index': index,
            'address': address.decode(),
            'balance': balance,
            'checksum': checksum
        })

        self.account.update_data(account_clone)

    def address_balance(self, address):
        node = self.account.settings.host
        api = Iota(node)
        gna_result = api.get_balances([Address(address).address])
        balance = gna_result['balances']
        return balance[0]

    def update_addresses_balance(self, start_index=0):
        max_index = 0
        for data in self.account.address_data:
            index = data['index']
            if start_index <= index:
                address = str(data['address'])
                balance = self.address_balance(address)
                self.write_address_data(index, address, balance)

            if max_index < index:
                max_index = index

        if max_index < start_index:
            pretty_print(
                'Start index was not found.'
                ' You should generate more addresses'
                ' or use a lower start index',
                color='red'
            )

    def update_fal_balance(self):
        index_with_value = []
        for data in address_data:
            if data['balance'] > 0:
                index = data['index']
                index_with_value.append(index)

        if len(index_with_value) > 0:
            f_index = min(index_with_value)
            l_index = max(index_with_value)
            write_fal_balance(f_index, l_index)

    def get_standard_account_info(self):
        address_count = len(self.account.data.address_data)
        self.update_addresses_balance(self.account.fal_balance['f_index'])
        self.update_fal_balance()

        if address_count < 1:
            pretty_print(
                '\n\nThis seems to be the first time '
                'you are using this account with the CL wallet!\n'
                'If you are expecting balance on this account'
                ' you should scan for balance.\n'
                'Do you want to scan for balance?\n\n '
            )
            yes = yes_no_user_input()
            if yes:
                pretty_print(
                    '\n\nOkay great, I will generate addresses'
                    ' and check them for balance!\n'
                    'Please tell me how many addresses'
                    ' I should check. If you say 100\n'
                    'I will generate addresses until balance'
                    ' is found or until 100 addresses\n'
                    'have been generated.\n'
                    'So, whats the maximum number of '
                    'addresses I should check?\n\n'
                )
                prompt = 'Please enter the max number of addresses to check: '
                addresses_to_check = numbers_user_input(prompt)
                if addresses_to_check > 0:
                    find_balance(addresses_to_check)
                    self.get_standard_account_info()

                elif addresses_to_check == 0:
                    pretty_print('You entered 0! I won\'t check any addresses.', color='green')
            elif not yes:
                pretty_print(
                    '\nOkay, then I will just generate a deposit address.\n'
                    'In case you wan\'t to generate addresses'
                    ' after that, you can use the \'find balance\' command.\n'
                    'Generating deposit address...\n\n\n'
                )
                generate_addresses(1)
                self.get_standard_account_info()

        elif address_count > 0:
            all_address_data = ''
            total_balance = 0
            for p in address_data:
                balance = p['balance']
                address = p['address']
                checksum = p['checksum']
                integrity = verify_checksum(checksum, address)
                if balance > 0 and integrity:
                    total_balance += balance
                    data = 'Index: ' \
                           + str(p['index']) \
                           + '   ' + address \
                           + '   balance: ' \
                           + convert_units(balance) \
                           + '\n'
                    all_address_data += data

                elif not integrity:
                    total_balance += balance
                    data = 'Index: ' \
                           + str(p['index']) \
                           + '   Invalid Checksum!!!' \
                           + '\n'
                    all_address_data += data

            if total_balance > 0:
                pretty_print(all_address_data)
                pretty_print('\n' + 'Deposit address: ' + str(get_deposit_address()), color='blue')
                pretty_print('\nTotal Balance: ' + convert_units(total_balance))

            else:
                pretty_print('No addresses with balance!', color='red')
                pretty_print('\n' + 'Deposit address: ' + str(get_deposit_address()), color='blue')


