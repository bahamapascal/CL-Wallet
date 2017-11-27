import json
from helpers import fetch_user_input, pretty_print, yes_no_user_input
from messages import account


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
                        'fal_balance': {'f_index': 0, 'l_index': 0},
                        'transfers_data': []
                    }
                }

                node = self.grab_host()
                if node:
                    data['account_data']['settings']['host'] = node

                json.dump(data, account_data)

                return data

    def update_data(self, data):
        self.data = data

        self.update_data_file()

    def update_data_file(self):
        with open(self.file_name, 'w') as account_data:
            json.dump(self.data, account_data)
