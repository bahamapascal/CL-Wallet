from terminaltables import SingleTable
from helpers import pretty_print, yes_no_user_input, fetch_user_input, is_valid_address, is_py2, convert_units
from messages import transfer as transfer_console_messages, common as common_console_messages
from balance import Balance
from address_manager import AddressManager
from iota import Iota, ProposedTransaction, Address,\
    TryteString, Tag, Transaction


class Transfer:
    def __init__(self, account):
        self.account = account
        self.keep_alive = True
        self.prepared = []

        self.prepare()

    def prepare(self):
        while self.keep_alive:
            get_recipient_address = True

            while get_recipient_address:
                recipient_address = fetch_user_input(transfer_console_messages['receiving_address_prompt'])

                if len(recipient_address) == 81:
                    pretty_print(
                        transfer_console_messages['address_without_checksum_warning'],
                        color='blue'
                    )

                    yes = yes_no_user_input()
                    if yes:
                        get_recipient_address = False
                    else:
                        pretty_print(transfer_console_messages['address_with_checksum'])
                elif len(recipient_address) == 90:
                    is_valid = is_valid_address(recipient_address) if is_py2 else is_valid_address(
                        recipient_address.encode())
                    if is_valid:
                        get_recipient_address = False
                    else:
                        pretty_print(transfer_console_messages['invalid_address'], color='red')
                        pretty_print(common_console_messages['try_again'], color='red')
                else:
                    pretty_print(transfer_console_messages['invalid_address'])
                    pretty_print(transfer_console_messages['valid_address_info'])

            recipient_address = bytes(recipient_address) if is_py2 else bytes(recipient_address.encode())

            """
            Check if receive address is unspent.
            """

            api = Iota(
                self.account.data['account_data']['settings']['host'],
                self.account.seed
            )

            # result = dict(states, duration)
            result = api.were_addresses_spent_from([recipient_address])

            # If recipient address is not spent, allow transfer
            if not result['states'][0]:
                user_message = fetch_user_input(transfer_console_messages['enter_message_prompt'])

                user_tag = fetch_user_input(transfer_console_messages['enter_tag_prompt'])
                user_tag = bytes(user_tag) if is_py2 else bytes(user_tag.encode())

                transfer_value = self.get_user_input(self.prepared)

                txn = \
                    ProposedTransaction(
                        address=Address(
                            recipient_address
                        ),

                        message=TryteString.from_string(user_message),
                        tag=Tag(user_tag) if is_py2 else Tag(TryteString.from_bytes(user_tag)),
                        value=transfer_value,
                    )

                self.prepared.append(txn)
                pretty_print(transfer_console_messages['additional_transfer'])

                yes = yes_no_user_input()

                # If user does not wish to add another transfer
                # move to review step
                if not yes:
                    self.keep_alive = False

                    self.review()

            # Otherwise, block the transfer and ask user to re-enter recipient address
            else:
                pretty_print(transfer_console_messages['recipient_address_already_spent'], color='red')

                self.prepare()

    def get_user_input(self, prepared_transfers):
        pretty_print(transfer_console_messages['number_and_unit_prompt'])

        balance_manager = Balance(self.account)

        balance_manager.update_addresses_balance(self.account.data['account_data']['fal_balance']['f_index'])
        balance_manager.update_fal_balance()

        total_balance = 0
        for p in self.account.data['account_data']['address_data']:
            balance = int(p['balance'])
            total_balance += balance
        if len(prepared_transfers) > 0:
            for txn in prepared_transfers:
                value = int(txn.value)
                total_balance -= value

        ask_user = True

        while ask_user:
            user_input = fetch_user_input(transfer_console_messages['amount_to_send_prompt'])
            user_input = user_input.upper()
            user_input_as_list = list(user_input)

            allowed_characters = list('1234567890. IKMGT')
            allowed_for_numbers = list('1234567890.')
            allowed_for_units = list('iIkKmMgGtT')
            is_valid = True

            value = ''
            unit = ''
            i = 0
            while i < len(user_input_as_list):
                char = user_input_as_list[i]
                if char in allowed_characters:
                    if char in allowed_for_numbers:
                        value += char
                    elif char in allowed_for_units:
                        unit += char
                else:
                    is_valid = False
                i += 1
            if is_valid:
                try:
                    value = float(value)

                    if unit == 'I':
                        value = value
                        if 1 > value > 0:
                            pretty_print(
                                transfer_console_messages['invalid_amount'],
                                color='red'
                            )
                        elif value > total_balance:
                            available_balance = convert_units(
                                self.account.data['account_data']['settings']['units'],
                                total_balance
                            )

                            insufficient_message = transfer_console_messages['insufficient_balance']
                            pretty_print(
                                insufficient_message.format(str(available_balance)),
                                color='red'
                            )
                        else:
                            return int(value)

                    elif unit == 'KI':
                        value *= 1000
                        if 1 > value > 0:
                            pretty_print(
                                transfer_console_messages['invalid_amount'],
                                color='red'
                            )
                        elif value > total_balance:
                            available_balance = convert_units(
                                self.account.data['account_data']['settings']['units'],
                                total_balance
                            )

                            insufficient_message = transfer_console_messages['insufficient_balance']
                            pretty_print(
                                insufficient_message.format(str(available_balance)),
                                color='red'
                            )
                        else:
                            return int(value)

                    elif unit == 'MI':
                        value *= 1000000
                        if 1 > value > 0:
                            pretty_print(
                                transfer_console_messages['invalid_amount'],
                                color='red'
                            )
                        elif value > total_balance:
                            available_balance = convert_units(
                                self.account.data['account_data']['settings']['units'],
                                total_balance
                            )
                            insufficient_message = transfer_console_messages['insufficient_balance']

                            pretty_print(
                                insufficient_message.format(str(available_balance)),
                                color='red'
                            )
                        else:
                            return int(value)

                    elif unit == 'GI':
                        value *= 1000000000
                        if 1 > value > 0:
                            pretty_print(
                                transfer_console_messages['invalid_amount'],
                                color='red'
                            )
                        elif value > total_balance:
                            available_balance = convert_units(
                                self.account.data['account_data']['settings']['units'],
                                total_balance
                            )
                            insufficient_message = transfer_console_messages['insufficient_balance']

                            pretty_print(
                                insufficient_message.format(str(available_balance)),
                                color='red'
                            )
                        else:
                            return int(value)

                    elif unit == 'TI':
                        value *= 1000000000000
                        if 1 > value > 0:
                            pretty_print(
                                transfer_console_messages['invalid_amount'],
                                color='red'
                            )
                        elif value > total_balance:
                            available_balance = convert_units(
                                self.account.data['account_data']['settings']['units'],
                                total_balance
                            )
                            insufficient_message = transfer_console_messages['insufficient_balance']

                            pretty_print(
                                insufficient_message.format(str(available_balance)),
                                color='red'
                            )
                        else:
                            return int(value)
                    else:
                        pretty_print(
                            transfer_console_messages['invalid_unit_size'],
                            color='red'
                        )

                except Exception as e:
                    pretty_print(
                        transfer_console_messages['invalid_value'],
                        color='red'
                    )

            else:
                pretty_print(
                    transfer_console_messages['invalid_value'],
                    color='red'
                )

    def review(self):
        table_title = 'Review Transfers'
        table_data = [('Address', 'Value', 'Message', 'Tag')]

        for txn in self.prepared:
            address = str(txn.address)

            value = str(convert_units(
                self.account.data['account_data']['settings']['units'],
                int(txn.value)
            ))

            message = txn.message or '-'
            tag = txn.tag if txn.tag != ('9' * 27) else '-'

            table_data.append((address, value, message, tag))

        pretty_print(
            SingleTable(table_data, table_title).table,
            color='green'
        )

        pretty_print(transfer_console_messages['please_review_transfers'], color='blue')

        ask_user = True
        while ask_user:
            user_input = fetch_user_input(
                transfer_console_messages['enter_confirm_to_send_transfers'] +
                '\n' +
                transfer_console_messages['enter_cancel_to_cancel_transfers']
            )

            user_input = user_input.upper()

            if user_input == 'CONFIRM':
                pretty_print(transfer_console_messages['sending_transfers'])

                ask_user = False
                try:
                    self.send()
                except Exception as e:
                    pretty_print(common_console_messages['error_occurred'], color='red')

            elif user_input == 'CANCEL':
                pretty_print(transfer_console_messages['transfers_cancelled'], color='red')
                ask_user = False

            else:
                pretty_print(common_console_messages['invalid_command'], color='red')
                pretty_print(common_console_messages['try_again'], color='red')

    def get_inputs(self):
        inputs = []

        for p in self.account.data['account_data']['address_data']:
            balance = p['balance']

            if balance > 0:
                address = p['address']
                address = bytes(address) if is_py2 else address.encode()
                index = int(p['index'])
                inpt = Address(address, key_index=index, security_level=2)

                inputs.append(inpt)

        return inputs

    def send(self):
        pretty_print(transfer_console_messages['sending_transfer'])

        address_manager = AddressManager(self.account)

        change_addy = bytes(address_manager.get_deposit_address()) if is_py2 else address_manager.get_deposit_address().encode()

        api = Iota(
            self.account.data['account_data']['settings']['host'],
            self.account.seed
        )

        api.send_transfer(
            inputs=self.get_inputs(),
            depth=7,
            transfers=self.prepared,
            change_address=change_addy,
            min_weight_magnitude=self.account.data['account_data']['settings']['min_weight_magnitude']
        )

        pretty_print(transfer_console_messages['completed'], color='green')
