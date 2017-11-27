import json
from iota import Iota, ProposedTransaction, Address,\
    TryteString, Tag, Transaction
from helpers import pretty_print


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
        transfers_data = account_clone.account_data.transfers_data

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
        account_data = account.data.account_data
        node = account_data.settings.host
        address_data = account_data.address_data
        seed = account.seed
        transfers_data = account_data.transfers_data

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

        if self.full_history:
            # print_transaction_history(full_history)

        elif not self.full_history:
            #print_transaction_history(full_history)
