from iota import Iota
from helpers import pretty_print
from messages import balance as balance_console_messages
from helpers import convert_units


class Balance:
    def __init__(self, account):
        self.account = account

    def find_balance(self, count):
        '''
        
        Quick hack for avoiding circular imports        
        '''
        from address_manager import AddressManager

        max_gap = 3
        margin = 4
        i = 0
        balance_found = False
        pretty_print(balance_console_messages['generating_addresses'], color='green')

        while i < count and margin > 0:
            pretty_print(balance_console_messages['checking_addresses'.format(i + 1, count)], color='green')
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
                    pretty_print(
                        balance_console_messages['balance_found'.format(
                            index,
                            address,
                            convert_units(self.account.data['settings']['units'], balance)
                        )],
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
        api = Iota(self.account.data['account_data']['settings']['host'])
        gna_result = api.get_balances([address])
        balance = gna_result['balances']

        return balance[0]

    def write_fal_balance(self, f_index=0, l_index=0):
        account_clone = self.account.data.copy()

        if f_index > 0 and l_index > 0:
            account_clone.account_data.fal_balance['f_index'] = f_index
            account_clone.account_data.fal_balance['l_index'] = l_index

        elif f_index > 0:
            account_clone.account_data.fal_balance['f_index'] = f_index
        elif l_index > 0:
            account_clone.account_data.fal_balance['l_index'] = l_index
        else:
            return  # TODO: Improve this

        self.account.update_data(account_clone)
