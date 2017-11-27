import sys
import hashlib
from iota import Iota, ProposedTransaction, Address,\
    TryteString, Tag, Transaction
from iota.crypto.addresses import AddressGenerator
from pretty_print import colors, PrettyPrint
from replay import Replay
from keyboard_interceptor import KeyboardInterruptHandler

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

    pretty_print('Starting to replay your specified bundle. This might take a few second...', color='green')
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


def get_checksum(address):
    data = address + seed
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

'''
Verifies the integrity of a address
and returns True or False
'''


def verify_checksum(checksum, address):
    actual_checksum = get_checksum(address)
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
    if new_address_with_checksum == address_with_checksum:
        return True
    else:
        return False



