from helpers import pretty_print


class Help:
    def __init__(self):
        self.print_help()

    def print_help(self):
        return pretty_print('''Avaliable commands:

    'account info'
        Will show you each address containing balance, total balance and your deposit address.

    'full account info'
        Will show you all saved addresses and there corespoding balance.

    'find balance'
        Searches for the first address with balance within a user defined range(e.g. first 100 addresses)

    'generate new address'
        Generates one new addresses!

    'send transfer'
        Send one or more transfers

    'account history'
        Shows all confirmed transfers and all new transfers (from your saved account addreses)


    'full account history'
        Shows all transfers, including old non confirmed transfers (from your saved account addreses)

    'replay bundle'
        Re-attach transactions to a different part of the Tangle.
        [Usage]: replay [short_transaction_id]
        [Note]: You can look up the short_transaction_id from (account history) or (full account history) options.
        [Example]: replay 36

    'settings'
        Set the minWeightMagnitude and the Units used to display iota tokens (i,Ki,Mi,Gi,Ti)

    'log out'
        Log out of your account and login with a different seed

    'exit'
        Exit the wallet.

                ''')
