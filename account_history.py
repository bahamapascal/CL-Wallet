import time
import datetime
from operator import itemgetter
from iota import Iota, ProposedTransaction, Address,\
    TryteString, Tag, Transaction
from helpers import pretty_print, is_py2, address_checksum, get_decoded_string, convert_units
from messages import account_history as account_history_console_messages


class AccountHistory:
    def __init__(self, account, full=False):
        self.account = account
        self.full_history = full

        self.fetch_transactions()

    def write_transactions_data(
            self,
            transaction_hash,
            is_confirmed,
            timestamp,
            tag,
            address,
            message,
            value,
            bundle,
            short_transaction_id
    ):
        account_clone = self.account.data.copy()
        transfers_data = account_clone['account_data']['transfers_data']

        for p in transfers_data:
            if p['transaction_hash'] == transaction_hash:
                if is_confirmed == p['is_confirmed']:
                    return
                else:
                    p['is_confirmed'] = is_confirmed
                    self.account.update_data(account_clone)
                    return

        transfers_data.append({
            'transaction_hash': transaction_hash,
            'is_confirmed': is_confirmed,
            'timestamp': timestamp,
            'tag': tag,
            'address': address,
            'message': message,
            'value': value,
            'bundle': bundle,
            'short_transaction_id': short_transaction_id
        })

        self.account.update_data(account_clone)

    def fetch_transactions(self):
        account = self.account
        account_data = account.data['account_data']
        node = account_data['settings']['host']
        address_data = account_data['address_data']
        seed = account.seed
        transfers_data = account_data['transfers_data']

        api = Iota(node, seed)
        address_count = len(address_data)
        all_txn_hashes = []
        saved_txn_hashes = []
        new_txn_hashes = []
        i = 0
        short_t_id_start_idx = 0

        while i < address_count:
            address = address_data[i]['address']
            address_as_versionsed = str(address) if is_py2 else bytes(address.encode())
            raw_transfers = api.find_transactions(addresses=[Address(address_as_versionsed).address])
            transactions_to_check = raw_transfers['hashes']

            for txn_hash in transactions_to_check:
                txn_hash = str(txn_hash)
                all_txn_hashes.append(txn_hash)
            i += 1

        for txn_hash in transfers_data:
            """
            Check if there is already a short transaction id assigned previously.
            If there is we'll assign the next id to start from
            """
            if txn_hash['short_transaction_id'] >= short_t_id_start_idx:
                short_t_id_start_idx = txn_hash['short_transaction_id'] + 1

            txn_hash = str(txn_hash['transaction_hash'])
            saved_txn_hashes.append(txn_hash)

        for txn_hash in all_txn_hashes:
            if txn_hash not in saved_txn_hashes:
                new_txn_hashes.append(txn_hash)

        if len(new_txn_hashes) > 0:
            pretty_print(
                'Retrieving and saving transfer data from '
                + str(len(new_txn_hashes))
                + ' transaction(s)!\n'
                  'Please wait...\n',
                color='blue'
            )

            for txn_hash in new_txn_hashes:
                txn_hash_as_bytes = bytes(txn_hash) if is_py2 else bytes(txn_hash.encode())

                '''
                Needs to be integrated into new transactions as well
                '''

                li_result = api.get_latest_inclusion([txn_hash_as_bytes])
                is_confirmed = li_result['states'][txn_hash]

                gt_result = api.get_trytes([txn_hash_as_bytes])
                trytes = str(gt_result['trytes'][0])
                txn = Transaction.from_tryte_string(trytes)
                timestamp = str(txn.timestamp)
                tag = str(txn.tag)
                address = str(txn.address)
                short_transaction_id = short_t_id_start_idx

                short_t_id_start_idx += 1  # increment short transaction id

                '''
                Placeholder until message decoding is added
                '''
                message = 'some message'
                value = str(txn.value)
                bundle = str(txn.bundle_hash)

                self.write_transactions_data(
                    txn_hash,
                    is_confirmed,
                    timestamp,
                    tag,
                    address,
                    message,
                    value,
                    bundle,
                    short_transaction_id
                )

        self.render_history()

    def render_history(self):
        account = self.account
        account_data = account.data['account_data']
        transfers_data = account_data['transfers_data']

        current_unix_time = time.time()
        '''
        Sort the transactions by timestamp
        '''

        sorted_transactions = sorted(transfers_data, key=itemgetter('timestamp'))
        addresses_with_new_transactions = []
        addresses_with_confirmed_transactions = []
        all_transactions = []
        new_transactions = []
        old_confirmed_transactions = []

        for addy in sorted_transactions:
            timestamp = addy['timestamp']
            is_confirmed = str(addy['is_confirmed'])
            if int(current_unix_time) - int(timestamp) < 25200:
                address = address_checksum(str(addy['address']))
                addresses_with_new_transactions.append(address)
            elif is_confirmed == 'True':
                address = address_checksum(str(addy['address'])) if is_py2 else address_checksum(
                    (addy['address'].encode()))
                addresses_with_confirmed_transactions.append(address)

        addresses_with_confirmed_transactions = set(
            addresses_with_confirmed_transactions
        )

        addresses_with_confirmed_transactions = list(
            addresses_with_confirmed_transactions
        )

        addresses_with_new_transactions = set(
            addresses_with_new_transactions
        )

        addresses_with_new_transactions = list(
            addresses_with_new_transactions
        )

        for transaction in sorted_transactions:
            timestamp = int(transaction['timestamp'])
            txn_time = datetime.datetime.fromtimestamp(
                int(timestamp)
            ).strftime('%Y-%m-%d %H:%M:%S')
            is_confirmed = str(transaction['is_confirmed'])
            transaction_hash = transaction['transaction_hash']
            address = address_checksum(str(transaction['address'])) if is_py2 \
                else address_checksum(transaction['address'].encode())
            bundle = transaction['bundle']
            tag = transaction['tag']
            value = transaction['value']
            short_transaction_id = transaction['short_transaction_id']

            if self.full_history:
                data = {'txn_time': str(txn_time),
                        'address': str(address),
                        'transaction_hash': str(transaction_hash),
                        'value': str(value),
                        'tag': str(tag),
                        'bundle': str(bundle),
                        'is_confirmed': str(is_confirmed),
                        'short_transaction_id': str(short_transaction_id)
                        }

                all_transactions.append(data)

            elif current_unix_time - timestamp < 25200:
                data = {
                    'txn_time': str(txn_time),
                    'address': str(address),
                    'transaction_hash': str(transaction_hash),
                    'value': str(value),
                    'tag': str(tag),
                    'bundle': str(bundle),
                    'is_confirmed': str(is_confirmed),
                    'short_transaction_id': str(short_transaction_id)
                    }

                new_transactions.append(data)

            elif is_confirmed == 'True':
                data = {
                    'txn_time': str(txn_time),
                    'transaction_hash': str(transaction_hash),
                    'address': str(address),
                    'value': str(value),
                    'bundle': str(bundle),
                    'tag': str(tag),
                    'short_transaction_id': str(short_transaction_id)
                    }

                old_confirmed_transactions.append(data)

        if len(new_transactions) > 0 and not self.full_history:
            pretty_print(account_history_console_messages['account_history_console_messages'])

            for addy in addresses_with_new_transactions:
                addy = address_checksum(str(addy) if is_py2 else bytes(addy))

                tx_to_from_info_message = account_history_console_messages['transactions_to_from']
                pretty_print(tx_to_from_info_message.format(get_decoded_string(addy)))

                for data in new_transactions:
                    address = data['address']
                    condition = address == addy if is_py2 else address == str(addy)

                    if condition:
                        txn_time = data['txn_time']
                        transaction_hash = data['transaction_hash']
                        value = data['value']
                        bundle = data['bundle']
                        tag = data['tag']
                        is_confirmed = data['is_confirmed']
                        short_transaction_id = data['short_transaction_id']

                        # TODO: Use terminal tables here
                        pretty_print(
                            '' + txn_time + '\n' +
                            '    Txn Hash: '
                            + transaction_hash + '  ' +
                            str(convert_units(
                                self.account.data['account_data']['settings']['units'],
                                value
                            )) + '\n' +
                            '    Bundle: ' + bundle + '\n' +
                            '    Tag: ' + tag + '\n' +
                            '    Confirmed: ' + is_confirmed + '\n' +
                            '    Short Transaction ID: ' + short_transaction_id + '\n'
                        )

        if len(old_confirmed_transactions) > 0 and not self.full_history:
            pretty_print(account_history_console_messages['old_transactions'])

            for addy in addresses_with_confirmed_transactions:
                addy = address_checksum(str(addy)) if is_py2 else address_checksum(addy)

                tx_to_from_info_message = account_history_console_messages['transactions_to_from']
                pretty_print(tx_to_from_info_message.format(get_decoded_string(addy)))

                for data in old_confirmed_transactions:
                    address = data['address']
                    condition = address == addy if is_py2 else address == str(addy)

                    if condition:
                        txn_time = data['txn_time']
                        transaction_hash = data['transaction_hash']
                        value = data['value']
                        bundle = data['bundle']
                        tag = data['tag']
                        short_transaction_id = data['short_transaction_id']
                        pretty_print(
                            ' ' + txn_time + '\n' +
                            '    Txn Hash: ' + transaction_hash +
                            '  ' + str(
                                convert_units(
                                    self.account.data['account_data']['settings']['units'],
                                    value
                            )) + '\n' +
                            '    Bundle: ' + bundle + '\n' +
                            '    Tag: ' + tag + '\n' +
                            '    Short Transaction ID: ' + short_transaction_id + '\n'
                        )

        if len(new_transactions) == 0 and \
                len(old_confirmed_transactions) == 0 and \
                len(all_transactions) == 0:

            pretty_print(account_history_console_messages['no_transactions_history'], color='red')

        elif self.full_history:
            pretty_print(account_history_console_messages['full_transactions_history'])

            for data in all_transactions:
                address = data['address']
                txn_time = data['txn_time']
                transaction_hash = data['transaction_hash']
                value = data['value']
                bundle = data['bundle']
                tag = data['tag']
                is_confirmed = data['is_confirmed']
                short_transaction_id = data['short_transaction_id']
                pretty_print(
                    ' ' + txn_time + '\n' +
                    ' To/From: ' + address + '\n'
                                             '          Txn Hash: ' +
                    transaction_hash + '  ' +
                    str(
                        convert_units(
                            self.account.data['account_data']['settings']['units'],
                            value
                        )) + '\n' +
                    '          Bundle: ' + bundle + '\n' +
                    '          Tag: ' + tag + '\n' +
                    '          Confirmed: ' + is_confirmed + '\n' +
                    '          Short Transaction ID: ' + short_transaction_id + '\n'
                )
