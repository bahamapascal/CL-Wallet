import sys
import hashlib
try:
    from urlparse import urlparse
except ImportError:
    # for py3
    from urllib.parse import urlparse

from iota import Iota, ProposedTransaction, Address,\
    TryteString, Tag, Transaction
from pretty_print import colors, PrettyPrint
from replay import Replay
from promote import Promote
from keyboard_interceptor import KeyboardInterruptHandler
from messages import helpers as helpers_console_messages
from balance import Balance

_ver = sys.version_info

is_py2 = (_ver[0] == 2)

is_py3 = (_ver[0] == 3)


def fetch_user_input(text):
    """
    Gets raw user input.

    :param text:
      str

    :return:
      input | raw_input
    """

    if is_py2:
        return raw_input(text)

    return input(text)


def pretty_print(text, *args, **kwargs):
    """
    Wrapper for PrettyPrint class.

    :param text:
      str

    :return:
      PrettyPrint
    """

    if 'color' in kwargs:
        # Might need to check if its a supported color
        return PrettyPrint(text, *args, **dict(kwargs, color=colors[kwargs['color']]))

    return PrettyPrint(text, *args, **kwargs)


def find_bundle_hash_for_short_transaction_id(id, transactions):
    """
    Given a short transaction id for a transaction, finds its bundle hash.

    :param id:
      str: Short transaction id.

    :param transactions:
      list: Transactions list.

    :return:
      str: Bundle hash
    """

    bundle = None
    if not transactions:
        return None

    for tx in transactions:
        id_as_string = str(tx['id'])

        if id_as_string == id:
            bundle = tx['bundle']
            break

    return bundle


def handle_promotion(node, command, transfers, **kwargs):
    """
     Handles transaction promotion.

     :param node:
       str: Selected IRI node.

     :param command:
       str: User's entered command.

     :param transfers:
        list: Transactions list.

     :return:
       Promote
    """

    # Check if a valid command
    arguments = command.split(' ', 1)
    t_id = None

    try:
        t_id = arguments[1]
    except IndexError:
        return pretty_print('Invalid command - See example usage.')

    bundle = find_bundle_hash_for_short_transaction_id(t_id.strip(), transfers)

    if bundle is None:
        return pretty_print(
            'Looks like there is no bundle associated with your specified short transaction id. Please try again'
        )

    pretty_print('Starting to promote your specified bundle. This might take a few seconds...', color='green')
    return Promote(
        node,
        bundle,
        alert_callback=lambda message: pretty_print(message, color='blue'),
        **kwargs
    )


def handle_replay(node, seed, command, transfers, **kwargs):
    """
     Handles transaction replay/reattach.

     :param node:
       str: Selected IRI node.

     :param seed:
       str: User's seed.

     :param command:
        str: User's entered command.

     :param transfers:
        list: Transactions list.

     :return:
       Replay
    """

    # Check if a valid command
    arguments = command.split(' ', 1)
    t_id = None

    try:
        t_id = arguments[1]
    except IndexError:
        return pretty_print('Invalid command - See example usage.')

    bundle = None
    t_id = t_id.strip()

    if not transfers:
        return pretty_print('Looks like you do not have any account history.')

    for transfer in transfers:
        id_as_string = str(transfer['id'])

        if id_as_string == t_id:
            bundle = transfer['bundle']
            break

    if bundle is None:
        return pretty_print(
            'Looks like there is no bundle associated with your specified short transaction id. Please try again'
        )

    pretty_print('Starting to replay your specified bundle. This might take a few seconds...', color='green')

    return Replay(
        node,
        seed,
        bundle,
        replay_callback=lambda message: pretty_print(message, color='blue'),
        **kwargs
    )


def intercept_keyboard_interrupts(callback):
    """
     Returns an instance of KeyboardInterruptHandler class.

     :param callback:
       function

     :return:
       KeyboardInterruptHandler
    """

    return KeyboardInterruptHandler(callback)


def is_string(string):
    """
     Checks if provided param is of type str.

     :param string:
       str

     :return:
       bool
    """

    return isinstance(string, basestring) if is_py2 else isinstance(string, str)


def confirms(value):
    """
     Wrapper function for checking if a user inputs "yes" or "y".

     :param value:
       str

     :return:
       bool
    """

    as_lower = value.lower() if is_string(value) else str(value).lower()
    return as_lower == 'y' or as_lower == 'yes'


def get_decoded_string(string):
    """
     Gets a decoded string.

     :param string:
       str: Any string.

     :return:
       str: Decoded string.
    """

    if is_py2:
        return str(string)
    else:
        if hasattr(string, 'decode'):
            return string.decode()

        return string


def create_seed_hash(seed):
    """
     Gets a SHA256 hash of seed.

     :param seed:
       str: Seed.

     :return:
       str: Hash of seed
    """

    return hashlib.sha256(seed.encode('utf-8')).hexdigest()


def get_checksum(address, seed):
    """
     Gets a SHA256 hash of address & seed.

     :param address:
       str: Address.

     :param seed:
       str: seed.

     :return:
       str: Hash of seed + address
    """

    data = address + seed
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def verify_checksum(checksum, address, seed):
    """
     Verifies address checksum.

     :param checksum:
       str: Address checksum.

     :param address:
       str: Address.

     :param seed:
       str: Seed

     :return:
       bool
    """

    actual_checksum = get_checksum(address, seed)

    return actual_checksum == checksum


def yes_no_user_input():
    """
     Asks the user for a yes or no
     and returns True or False accordingly.

     :return:
       None
    """

    while True:
        yes_no = fetch_user_input('Enter Y for yes or N for no: ')
        yes_no = yes_no.lower()
        if yes_no == 'n' or yes_no == 'no':
            return False
        elif yes_no == 'y' or yes_no == 'yes':
            return True
        else:
            pretty_print(
                'Ups seems like you entered something'
                'different then "Y" or "N" '
            )


def address_checksum(address):
    """
     Takes a address (81 Characters) and
     converts it to an address with checksum (90 Characters).

     :param address:
       str: Address.

     :return:
       str: Address checksum
    """

    address = get_decoded_string(address)
    bytes_address = bytes(address) if is_py2 else bytes(address, 'utf8')
    addy = Address(bytes_address)
    return str(addy.with_valid_checksum()) if is_py2 else bytes(addy.with_valid_checksum())


def is_valid_address(address_with_checksum):
    """
     Validates address.

     :param address_with_checksum:
       str: Address with checksum.

     :return:
       bool
    """

    address = address_with_checksum[:81]
    new_address_with_checksum = address_checksum(address)

    return new_address_with_checksum == address_with_checksum


def numbers_user_input(prompt):
    """
     Asks the user to enter a number and will
     only accept the user input if it's a valid number.

     :param prompt:
       str: Message.

     :return:
       None
    """

    while True:
        user_input = fetch_user_input(prompt)
        number = user_input.isdigit()
        if number:
            return int(user_input)
        elif not number:
            pretty_print(helpers_console_messages['invalid_number'], color='red')


def convert_units(unit, value):
    """
     Converts IOTAs into the unit that is set
     in the account settings and returns a string.

     :param unit:
       Selected IOTA unit.

     :param value:
       IOTA value.

     :return:
       str: Returns value with corresponding unit.
     """

    value = float(value)

    if unit == 'i':
        value = str(int(value)) + 'i'
        return value
    elif unit == 'ki':
        value = '{0:.3f}'.format(value / 1000)
        value = str(value + 'Ki')
        return value
    elif unit == 'mi':
        value = '{0:.6f}'.format(value / 1000000)
        value = str(value) + 'Mi'
        return value
    elif unit == 'gi':
        value = '{0:.9f}'.format(value / 1000000000)
        value = str(value + 'Gi')
        return value
    elif unit == 'ti':
        value = '{0:.12f}'.format(value / 1000000000000)
        value = str(value + 'Ti')
        return value


def find_balance(account):
    """
    Finds balance on addresses.

    :param account:
      Account class instance.

    :return:
      None
    """

    pretty_print(helpers_console_messages['balance_finder_general'])

    count = numbers_user_input(helpers_console_messages['balance_finder_address_number_prompt'])

    balance = Balance(account)

    return balance.find_balance(count)


def is_valid_uri(uri):
    """
    :param uri:
        uri to validate

    :return:
        boolean
    """
    try:
        result = urlparse(uri)
        return result.scheme and result.netloc
    except:
        return False


def get_input_transactions(transactions):
    """
    Given a list of transactions for a bundle, filters input transactions.

    :param transactions:
      list: Transactions.

    :return:
      list: List of input transactions.
    """

    input_transactions = []

    for tx in transactions:
        if tx.value < 0:
            input_transactions.append(tx)

    return input_transactions


def get_output_transactions(transactions):
    """
    Given a list of transactions for a bundle, filters output transactions.

    :param transactions:
      list: Transactions.

    :return:
      list: List of output transactions.
    """

    output_transactions = []

    for tx in transactions:
        if tx.value >= 0:
            output_transactions.append(tx)

    return output_transactions


def get_tail_transaction(transactions):
    """
    Given a list of transactions for a bundle, gets tail transaction.

    :param transactions:
      list: Transactions.

    :return:
      dict: Tail transaction.
    """

    tail_transaction = {}

    for tx in transactions:
        if tx.current_index == 0:
            tail_transaction = tx
            break

    return tail_transaction
