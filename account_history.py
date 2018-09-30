import time
from datetime import datetime
from terminaltables import SingleTable
from iota import Iota, ProposedTransaction, Address,\
    TryteString, Tag, Transaction, Bundle, BundleHash
from helpers import pretty_print, convert_units, get_input_transactions, get_output_transactions,\
    get_tail_transaction
from address_manager import AddressManager
from messages import account_history as account_history_messages


class AccountHistory:
    """
    Contains transaction history.
    """

    def __init__(self, account, full=False):
        """
        Account class instance.
        """

        self.account = account

        """
        Decides whether to display full/partial account history to the console 
        """
        self.full_history = full

        self.fetch_transactions()

    def fetch_transactions(self):
        """
        Fetch transactions from the tangle

        :return:
            None
        """

        # Extract needed information from account
        account = self.account.data.copy()
        account_data = account['account_data']
        node = account_data['settings']['host']
        seed = self.account.seed
        stored_transactions_hashes = account_data['hashes']
        transactions_data = account_data['transfers_data']

        api = Iota(node, seed)

        bundles = {}

        for tx in transactions_data:
            bundles[tx['bundle']] = tx

        # Get stored addresses
        addresses = AddressManager(self.account).get_addresses()

        # First find transactions against all generated addresses
        transactions_result = api.find_transactions(addresses=addresses)

        if len(transactions_result['hashes']) > len(stored_transactions_hashes):
            hashes_to_search = list(set(transactions_result['hashes']) - set(stored_transactions_hashes))

            # Update hashes
            account_data['hashes'] = transactions_result['hashes']

            # Get trytes
            transaction_trytes = api.get_trytes(hashes=hashes_to_search)

            # Convert trytes -> transaction objects
            transaction_objects = []

            for tryte in transaction_trytes['trytes']:
                transaction_objects.append(Transaction.from_tryte_string(tryte))

            # Filter tail transactions hashes
            tail_transaction_hashes = []

            for tx in transaction_objects:
                if tx.current_index == 0:
                    tail_transaction_hashes.append(tx.hash)

            for index, tail_transaction_hash in enumerate(tail_transaction_hashes):
                try:
                    result = api.get_bundles(tail_transaction_hash)
                    for value in result['bundles']:
                        bundle_hash = BundleHash(value.hash)

                        if bundle_hash in bundles:
                            bundles[bundle_hash]['tail_transactions'].append(
                                get_tail_transaction(value.transactions).hash
                            )
                        else:
                            inputs = [{
                                'address': Address(i.address).address,
                                'value': i.value,
                                'current_index': i.current_index,
                                'last_index': i.last_index,
                                'hash': i.hash
                            } for i in get_input_transactions(value.transactions)]

                            output_transactions = get_output_transactions(value.transactions)

                            outputs = [{
                                'address': Address(output.address).address,
                                'value': output.value,
                                'current_index': output.current_index,
                                'last_index': output.last_index,
                                'hash': output.hash
                            } for output in output_transactions]

                            # Get tag from bundle
                            tag = str(output_transactions[0].tag.decode())

                            # Get timestamp from bundle
                            timestamp = output_transactions[0].timestamp

                            # Get transaction message
                            messages = [str(message) for message in value.get_messages()]
                            message = messages[0] if len(messages) else \
                                account_history_messages['no_transaction_message']

                            bundles[bundle_hash] = {
                                'bundle': bundle_hash,
                                'inputs': inputs,
                                'outputs': outputs,
                                'tail_transactions': [get_tail_transaction(value.transactions).hash],
                                'id': index + len(transactions_data),
                                'tag': tag,
                                'timestamp': timestamp,
                                # Initialize by false
                                'is_confirmed': False,
                                'message': message
                            }
                except Exception:
                    pass

            updated_transactions = []

            for key in bundles:
                bundle = bundles[key]

                # Only check confirmation states for pending transactions
                if bundle['is_confirmed'] is False:
                    # Check confirmation states for both original plus reattachments
                    inclusion_states = api.get_latest_inclusion(bundle['tail_transactions'])

                    bundle['is_confirmed'] = any(
                        inclusion_states['states'][tx_hash] is True for tx_hash in bundle['tail_transactions']
                    )

                # Append all bundles as this is the updated list that would be overridden
                updated_transactions.append(bundle)

            account_data['transfers_data'] = updated_transactions

            self.account.update_data(account)
        else:
            pretty_print(account_history_messages['no_transactions_history'])

        self.render_history(account_data['transfers_data'])

    def render_history(self, transactions):
        """
         Displays transaction history to the console.

         :param transactions:
           List of transactions.

         :return:
           None
         """

        current_unix_time = time.time()
        selected_iota_units = self.account.data['account_data']['settings']['units']

        # If command is full history then, display all transactions to console
        # Otherwise display recent transactions & confirmed transactions to the console
        for tx in transactions if self.full_history else [
            tx for tx in transactions if tx['is_confirmed'] or current_unix_time - tx['timestamp'] < 25200
        ]:
            table_title = account_history_messages['transaction']
            table_data = []

            input_data = ''
            output_data = ''

            for input in tx['inputs']:
                if input_data:
                    input_data = input_data + '\n\n' + 'Address:' + str(input['address']) + '\n' +\
                                 'Hash:' + str(input['hash']) + '\n' + 'Value:' + \
                                 convert_units(selected_iota_units, input['value'])
                else:
                    input_data = 'Address:' + str(input['address']) + '\n' + 'Hash:' + str(input['hash']) + '\n' + \
                                 'Value:' + convert_units(selected_iota_units, input['value'])

            for output in tx['outputs']:
                if output_data:
                    output_data = output_data + '\n\n' + 'Address:' + str(output['address']) +\
                                  '\n' + 'Hash:' + str(output['hash']) + '\n' + 'Value:' + \
                                  convert_units(selected_iota_units, output['value'])
                else:
                    output_data = 'Address:' + str(output['address']) + '\n' + 'Hash:' + str(output['hash']) + '\n' + \
                                  'Value:' + convert_units(selected_iota_units, output['value'])

            table_data.insert(len(table_data), ('Short Transaction ID', tx['id']))
            table_data.insert(len(table_data), ('Inputs', input_data))
            table_data.insert(len(table_data), ('Outputs', output_data))
            table_data.insert(len(table_data), ('Timestamp', datetime.utcfromtimestamp(tx['timestamp'])
                                                 .strftime('%Y-%m-%d %H:%M:%S')))
            table_data.insert(len(table_data), ('Confirmed', 'Confirmed' if tx['is_confirmed'] else 'Not Confirmed'))
            table_data.insert(len(table_data), ('Reattachments', len(tx['tail_transactions']) - 1))
            table_data.insert(len(table_data), ('Tag', str(tx['tag'])))

            table_data.insert(len(table_data), ('Message', str(tx['message'])))

            table_instance = SingleTable(table_data, table_title)
            table_instance.inner_row_border = True

            pretty_print(table_instance.table, color='blue')
