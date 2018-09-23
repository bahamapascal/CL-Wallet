from iota.json import JsonEncoder
import getpass
import json
from helpers import fetch_user_input, pretty_print, yes_no_user_input, is_py2, create_seed_hash
from messages import account


class Account:
    """
     Contains account related data.
     """

    def __init__(self, initial_settings):
        """
        Account seed
        """

        self.seed = None
        """
        Account file name
        """
        self.file_name = None

        """
        Account data
        """

        self.data = None

        self.login(initial_settings)

    def grab_host(self):
        """
        Gets IRI node uri from user as input.

        :return:
          str | None
        """

        pretty_print(account['welcome'])
        yes = yes_no_user_input()

        if yes:
            host = fetch_user_input(
                account['choose_host']
            )

            host_info_message = account['new_host_set']
            pretty_print(host_info_message.format(str(host)), color='blue')

            return host

        pretty_print(account['keeping_default_host'])
        return None

    def populate(self, settings):
        """
        Initialize account data

        :param settings:
          dict: Account settings.

        :return:
          dict: Account data.
        """

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
                        'transfers_data': [],
                        'hashes': []
                    }
                }

                node = self.grab_host()
                if node:
                    data['account_data']['settings']['host'] = node

                json.dump(data, account_data)

                return data

    def update_data(self, data):
        """
        Update account data in memory and in file

        :param data:
          dict: Account data.

        :return:
          None
        """

        self.data = data

        self.update_data_file()

    def update_data_file(self):
        """
        Update account data account file

        :return:
          None
        """

        with open(self.file_name, 'w') as account_data:
            json.dump(self.data, account_data, cls=JsonEncoder, indent=2)

    def create_file_name(self, seed):
        """
        Create account file

        :param seed:
          str: Seed.

        :return:
          str: File name.
        """

        seed_hash = create_seed_hash(seed)
        file_name = seed_hash[:12]
        file_name += '.txt'

        return file_name

    def login(self, initial_settings):
        """
        Gets user's seed as an input and proceed to command center

        :param initial_settings:
          dict: Default account settings.

        :return:
          None
        """

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
            entered_seed_info_message = account['entered_seed']
            pretty_print(entered_seed_info_message.format(seed))
        elif not yes:
            pretty_print(account['seed_display_prompt'], color='blue')

        self.data = self.populate(initial_settings)
