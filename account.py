import json
from helpers import fetch_user_input, pretty_print
from messages import account


def yes_no_user_input():
    while True:
        yes_no = fetch_user_input('Enter Y for yes or N for no: ')
        yes_no = yes_no.lower()
        if yes_no == 'n' or yes_no == 'no':
            return False
        elif yes_no == 'y' or yes_no == 'yes':
            return True
        else:
            pretty_print(
                'Ups seems like you entered something'
                'different then "Y" or "N" '
                )


class Account:
    def __init__(self, seed, file_name, initial_settings):
        self.seed = seed
        self.file_name = file_name

        self.data = self.populate(initial_settings)

    def grab_host(self):
        pretty_print(account['welcome'])
        yes = yes_no_user_input()

        if yes:
            host = fetch_user_input(
                '\nPlease enter the host'
                ' you want to connect to: '
            )

            pretty_print(
                '\nHost set to '
                + str(host)
                + '\n\n',
                color='blue'
            )

            return host

        pretty_print('Okay, I won\'t change the host!\n\n')
        return None

    def populate(self, settings):
        try:
            with open(self.file_name, 'r') as account_data:
                data = json.load(account_data)
                return data
        except:
            with open(self.file_name, 'w') as account_data:
                data = {
                    'account_data': {
                        'settings': settings,
                        'address_data': [],
                        'fal_balance': [{'f_index': 0, 'l_index': 0}],
                        'transfers_data': []
                    }
                }

                node = self.grab_host()
                if node:
                    data['account_data']['settings']['host'] = node

                json.dump(data, account_data)

                return data
