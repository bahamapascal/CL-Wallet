import getpass
import json
from helpers import fetch_user_input, pretty_print, yes_no_user_input, is_py2, create_seed_hash
from messages import account


class Account:
    def __init__(self, initial_settings):
        self.seed = None
        self.file_name = None
        self.data = None

        self.login(initial_settings)

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

    def create_file_name(self, seed):
        seed_hash = create_seed_hash(seed)
        file_name = seed_hash[:12]
        file_name += '.txt'

        return file_name

    def login(self, initial_settings):
        pretty_print(account['login_welcome'], color='green')

        password = getpass.getpass(account['enter_seed'])
        raw_seed = unicode(password) if is_py2 else str(password)
        raw_seed = raw_seed.upper()
        raw_seed = list(raw_seed)
        allowed = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ9')
        seed = ''
        i = 0
        while i < len(raw_seed) and i < 81:
            char = raw_seed[i]
            if char not in allowed:
                char = '9'
                seed += char
            else:
                seed += str(char)
            i += 1
        while len(seed) < 81:
            seed += '9'

        self.seed = seed
        self.file_name = self.create_file_name(seed)

        pretty_print(account['seed_hash'])
        pretty_print(create_seed_hash(seed), color='blue')
        pretty_print(account['seed_review'], color='red')

        yes = yes_no_user_input()
        if yes:
            pretty_print(account['entered_seed'.format(seed)])

        elif not yes:
            pretty_print(account['seed_display_prompt'], color='blue')

        self.data = self.populate(initial_settings)
