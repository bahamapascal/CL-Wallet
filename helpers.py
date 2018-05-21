import sys
import hashlib
from iota import Iota, ProposedTransaction, Address,\
    TryteString, Tag, Transaction
from iota.crypto.addresses import AddressGenerator
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
    if is_py2:
        return raw_input(text)

    return input(text)


def pretty_print(text, *args, **kwargs):
    if 'color' in kwargs:
        # Might need to check if its a supported color
        return PrettyPrint(text, *args, **dict(kwargs, color=colors[kwargs['color']]))

    return PrettyPrint(text, *args, **kwargs)


def find_bundle_hash_for_short_transaction_id(id, transactions):
    bundle = None
    if not transactions:
        return None

    for tx in transactions:
        id_as_string = str(tx['short_transaction_id'])

        if id_as_string == id:
            bundle = tx['bundle']
            break

    return bundle


def handle_promotion(node, command, transfers, **kwargs):
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
        id_as_string = str(transfer['short_transaction_id'])

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
    return KeyboardInterruptHandler(callback)


def is_string(string):
    return isinstance(string, basestring) if is_py2 else isinstance(string, str)


def confirms(value):
    """
    :param value: string
    :return boolean: 
    """
    as_lower = value.lower() if is_string(value) else str(value).lower()
    return as_lower == 'y' or as_lower == 'yes'


def get_decoded_string(string):
    if is_py2:
        return str(string)
    else:
        if hasattr(string, 'decode'):
            return string.decode()

        return string

'''
Returns a sha256 hash of the seed
'''


def create_seed_hash(seed):
    return hashlib.sha256(seed.encode('utf-8')).hexdigest()

'''
Returns a sha256 hash of seed + address
'''


def get_checksum(address, seed):
    data = address + seed
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

'''
Verifies the integrity of a address
and returns True or False
'''


def verify_checksum(checksum, address, seed):
    actual_checksum = get_checksum(address, seed)
    return actual_checksum == checksum

'''
Will ask the user for a yes or no
and returns True or False accordingly
'''


def yes_no_user_input():

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


'''
Takes a address (81 Characters) and
converts it to an address with checksum (90 Characters)
'''


def address_checksum(address):
    address = get_decoded_string(address)
    bytes_address = bytes(address) if is_py2 else bytes(address,'utf8')
    addy = Address(bytes_address)
    return str(addy.with_valid_checksum()) if is_py2 else bytes(addy.with_valid_checksum())


'''
Takes an address with checksum
and verifies if the address matches with the checksum
'''


def is_valid_address(address_with_checksum):
    address = address_with_checksum[:81]
    new_address_with_checksum = address_checksum(address)

    return new_address_with_checksum == address_with_checksum


'''
Asks the user to enter a number
and will only accept the user input
if it's a valid number
'''


def numbers_user_input(prompt):
    while True:
        user_input = fetch_user_input(prompt)
        number = user_input.isdigit()
        if number:
            return int(user_input)
        elif not number:
            pretty_print(helpers_console_messages['invalid_number'], color='red')


'''
Creates a unique file name by taking the first
12 characters of the sha256 hash from a seed
'''


def create_file_name():
    seed_hash = create_seed_hash(seed)
    file_name = seed_hash[:12]
    file_name += '.txt'
    return file_name



'''
If there is no account file for the entered seed,
ths function will ask the user for the node to connect to.
The node address is then saved in the account file
'''


'''
Converts Iotas into the unit that is set
in the account settings and returns a string
'''
# TODO: Need to have a default case


def convert_units(unit, value):
    value = float(value)

    if unit == 'i':
        value = str(int(value)) + 'i'
        return value
    elif unit == 'ki':
        value = '{0:.3f}'.format(value/1000)
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


"""
    Wraps Balance
"""


def find_balance(account):
    pretty_print(helpers_console_messages['balance_finder_general'])

    count = numbers_user_input(helpers_console_messages['balance_finder_address_number_prompt'])

    balance = Balance(account)

    return balance.find_balance(count)