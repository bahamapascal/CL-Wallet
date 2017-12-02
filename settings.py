from helpers import fetch_user_input, numbers_user_input, pretty_print
from messages import settings as console_messages


class Settings:
    def __init__(self, account):
        self.account = account
        self.keep_alive = False

        self.initialize()

    def initialize(self):
        self.keep_alive = True
        self.set_settings()

    def set_settings(self):
        pretty_print(console_messages['description_min_weight_magnitude'])
        pretty_print(console_messages['description_units'])
        pretty_print(console_messages['description_host'])
        pretty_print(console_messages['description_current_settings'])
        pretty_print(console_messages['description_back'])

        stay_in_settings = True
        while stay_in_settings:
            user_command_input = fetch_user_input(console_messages['command_input'])
            account_clone = self.account.data.copy()
            if user_command_input == 'min_weight_magnitude':
                account_clone['account_data']['settings']['min_weight_magnitude'] = numbers_user_input('\nPlease enter the minWeightMagnitude: ')
                self.account.update_data(account_clone)
                pretty_print(
                    'MinWeightMagnitude set to '
                    + str(account_clone['account_data']['settings']['min_weight_magnitude'])
                    + '\n\n',
                    color='blue'
                )

            elif user_command_input == 'unit':
                units = fetch_user_input('\nPlease enter "i","ki","mi","gi" or "ti": ')
                if units == 'i' \
                        or units == 'ki' \
                        or units == 'mi' \
                        or units == 'gi' \
                        or units == 'ti':
                    settings[0]['units'] = units
                    with open(file_name, 'w') as account_data:
                        json.dump(raw_account_data, account_data)
                    pretty_print(
                        'Units set to ' + str(settings[0]['units']) + '\n\n',
                        color='blue'
                    )

                else:
                    pretty_print(
                        '\n\nUps you seemed to have'
                        ' entered something else'
                        ' then "i","ki","mi","gi" or "ti" ',
                        color='red'
                    )
                    pretty_print(
                        'Please try again!\n\n',
                        color='green'
                    )

            elif user_command_input == 'host':
                settings[0]['host'] = fetch_user_input(
                    '\nPlease enter the'
                    ' host you want to connect to: '
                )
                with open(file_name, 'w') as account_data:
                    json.dump(raw_account_data, account_data)
                pretty_print(
                    'Host set to ' + str(settings[0]['host']) + '\n\n',
                    color='blue'
                )

            elif user_command_input == 'current_settings':
                min_weight_magnitude = settings[0]['min_weight_magnitude']
                units = settings[0]['units']
                host = settings[0]['host']
                pretty_print(
                    '\n\nMinWeightMagnitude is currently set to '
                    + str(min_weight_magnitude) + '\n' +
                    'Units are set to ' + str(units) + '\n' +
                    'Host is set to ' + str(host) + '\n\n',
                    color='blue'
                )

            elif user_command_input == 'back':
                stay_in_settings = False

            else:
                pretty_print(
                    'Ups I didn\'t understand'
                    ' that command. Please try again!',
                    color='red'
                )

