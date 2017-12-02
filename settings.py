from helpers import fetch_user_input, numbers_user_input, pretty_print
from messages import settings as console_messages, common as common_console_messages


class Settings:
    def __init__(self, account):
        self.account = account
        self.keep_alive = False

        self.initialize()

    def initialize(self):
        self.keep_alive = True
        self.manage_settings()

    def manage_settings(self):
        pretty_print(console_messages['description_min_weight_magnitude'])
        pretty_print(console_messages['description_units'])
        pretty_print(console_messages['description_host'])
        pretty_print(console_messages['description_current_settings'])
        pretty_print(console_messages['description_back'])

        while self.keep_alive:
            user_command_input = fetch_user_input(console_messages['command_input'])
            account_clone = self.account.data.copy()

            if user_command_input == 'min_weight_magnitude':
                account_clone['account_data']['settings']['min_weight_magnitude'] = numbers_user_input(console_messages['enter_min_weight_magnitude'])
                self.account.update_data(account_clone)
                pretty_print(console_messages['min_weight_magnitude_set'.format(str(account_clone['account_data']['settings']['min_weight_magnitude']))], color='blue')

            elif user_command_input == 'unit':
                units = fetch_user_input(console_messages['enter_units'])
                if units == 'i' \
                        or units == 'ki' \
                        or units == 'mi' \
                        or units == 'gi' \
                        or units == 'ti':
                    account_clone['account_data']['settings']['units'] = units
                    self.account.update_data(account_clone)
                    pretty_print(console_messages['units_set'.format(str(account_clone['account_data']['settings']['units']))], color='blue')

                else:
                    pretty_print(console_messages['invalid_unit'], color='red')
                    pretty_print(common_console_messages['try_again'], color='green')

            elif user_command_input == 'host':
                host = fetch_user_input(console_messages['enter_host'])
                # TODO: Do validation for host
                account_clone['account_data']['settings']['host'] = host
                self.account.update_data(account_clone)
                print host
                pretty_print(console_messages['host_set'.format(str(host))])

            elif user_command_input == 'current_settings':
                min_weight_magnitude = account_clone['account_data']['settings']['min_weight_magnitude']
                units = account_clone['account_data']['settings']['units']
                host = account_clone['account_data']['settings']['host']
                pretty_print(console_messages['current_settings'.format(str(min_weight_magnitude), str(units), str(host))])

            elif user_command_input == 'back':
                self.keep_alive = False

            else:
                pretty_print(common_console_messages['invalid_command'], color='red')

