import getpass
import hashlib
import json
import time
import datetime
from operator import itemgetter

print("\nStarting wallet...\n\n\n\n")

from iota import Iota, ProposedTransaction, Address, TryteString, Tag, Transaction
from iota.crypto.addresses import AddressGenerator
from iota.commands.extended.utils import get_bundles_from_transaction_hashes
import iota.commands.extended.get_latest_inclusion
from iota.json import JsonEncoder


# Returns a sha256 hash of the seed
def create_seed_hash(seed):
    s = hashlib.sha256(seed)
    return s.hexdigest()


# Returns a sha256 hash of seed + address
def get_checksum(address):
    data = address + seed
    s = hashlib.sha256(data)
    return s.hexdigest()


# Verifys the integrety of a address and returns True or False
def verify_checksum(checksum, address):
    actual_checksum = get_checksum(address)
    if actual_checksum == checksum:
        return True
    else:
        return False


# Will ask the user for a yes or no and returns True or False accordingly
def yes_no_user_input():

    while True:
        yes_no = raw_input("Enter Y for yes or N for no: ")
        yes_no = yes_no.lower()
        if yes_no == "n" or yes_no == "no":
            return False
        elif yes_no == "y" or yes_no == "yes":
            return True
        else:
            print("""Ups seems like you entered something different then "Y" or "N" """)


# Askes the user to enter a number and will only accept the user input if it's a valid number
def numbers_user_input(prompt):

    while True:
        user_input = raw_input(prompt)
        number = user_input.isdigit()
        if number:
            return int(user_input)
        elif not number:
            print("You didn't enter a number")


# Creates a unique file name by taking the first 12 characters of the sha256 hash from a seed
def create_file_name():
    seed_hash = create_seed_hash(seed)
    file_name = seed_hash[:12]
    file_name += ".txt"
    return file_name


# The login screen; Will make sure that only a valid seed is enterd
def log_in():
    print("\n\n\n------------------------------------------------Account login---------------------------------------"
          "-----------------"
          "\n\nA seed should only contain the letters A-Z and 9. Lowercase letters will automaticaly be coverted to\n"
          "uppercase and everything else that is not A-Z, will be convertet to a 9.")
    raw_seed = unicode(getpass.getpass("\n \nPlease enter your seed to login to your account: "))
    raw_seed = raw_seed.upper()
    raw_seed = list(raw_seed)
    allowed = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ9")
    seed = ""
    i = 0
    while i < len(raw_seed) and i < 81:
        char = raw_seed[i]
        if char not in allowed:
            char = "9"
            seed += char
        else:
            seed += str(char)
        i += 1
    while len(seed) < 81:
        seed += "9"

    print("\n\nThe Sha256 hash of your seed is:")
    print(create_seed_hash(seed))

    print("Should the seed be displayed for review?\n")

    yes = yes_no_user_input()
    if yes:
        print("You entered " + seed + " as seed.")

    elif not yes:
        print("OK, seed won't be displayed!")

    return seed


# If there is no account file for the entered seed, ths function will ask the user for the node to connect to.
# The node address is then saved in the account file
def first_login_prompt(data):
    print("\n\nSeems like its your first time logging in to this seed!\n"
          "By default the wallet will connect to testnet node \"http://bahamapascal-tn1.ddns.net:14200"
          " (while in Beta)\"\n"
          "Do you want to connect to another host?\n\n")
    yes = yes_no_user_input()

    if yes:
        data['account_data'][0]['settings'][0]['host'] = raw_input("\nPlease enter the host you want to connect to: ")

        print("\nHost set to " + str(data['account_data'][0]['settings'][0]['host']) + "\n\n")
        return data

    else:
        print("Okay, I won't change the host!\n\n")
        return data


# Will try to open the account file. In case the file doesn't exist it will create a new account file.
def read_account_data():
    try:

        with open(file_name, 'r') as account_data:
            data = json.load(account_data)
            return data
    except:
        with open(file_name, 'w') as account_data:
            data = {}
            data['account_data'] = []
            data['account_data'].append({
                'settings': [{'host': "http://bahamapascal-tn1.ddns.net:14200", 'min_weight_magnitude': 13, 'units': "i"}],
                'address_data': [],
                'fal_balance': [{'f_index': 0, 'l_index': 0}],
                'transfers_data': []
            })
            data = first_login_prompt(data)
            json.dump(data, account_data)
            print("Created new account file!")
            return data


# Settings menu where the user can set account specific settings. The settings are saved in the account file
def set_settings():
    print("""Enter "min_weight_magnitude" to set the minWeightMagnitude""")
    print("""Enter "unit" to set the Units used to display iota tokens (i,Ki,Mi,Gi,Ti)""")
    print("""Enter "host" to set a new host to connect to""")
    print("""Enter "current_settings" to see """)
    print("""Enter "back" to quit the settings menu\n\n""")

    stay_in_settings = True
    while stay_in_settings:
        user_command_input = raw_input("Please enter a command: ")

        if user_command_input == "min_weight_magnitude":
            settings[0]['min_weight_magnitude'] = numbers_user_input("\nPlease enter the minWeightMagnitude: ")
            with open(file_name, 'w') as account_data:
                json.dump(raw_account_data, account_data)
            print("MinWeightMagnitude set to " + str(settings[0]['min_weight_magnitude']) + "\n\n")

        elif user_command_input == "unit":
            units = raw_input("""\nPlease enter "i","ki","mi","gi" or "ti": """)
            if units == "i" or units == "ki" or units == "mi" or units == "gi" or units == "ti":
                settings[0]['units'] = units
                with open(file_name, 'w') as account_data:
                    json.dump(raw_account_data, account_data)
                print("Units set to " + str(settings[0]['units']) + "\n\n")

            else:
                print("""\n\nUps you seemed to have entered something else then "i","ki","mi","gi" or "ti" """)
                print("Please try again!\n\n")

        elif user_command_input == "host":
            settings[0]['host'] = raw_input("\nPlease enter the host you want to connect to: ")
            with open(file_name, 'w') as account_data:
                json.dump(raw_account_data, account_data)
            print("Host set to " + str(settings[0]['host']) + "\n\n")

        elif user_command_input == "current_settings":
            min_weight_magnitude = settings[0]['min_weight_magnitude']
            units = settings[0]['units']
            host = settings[0]['host']
            print("\n\nMinWeightMagnitude is currently set to " + str(min_weight_magnitude) + "\n" +
                  "Units are set to " + str(units) + "\n" +
                  "Host is set to " + str(host) + "\n\n")

        elif user_command_input == "back":
            stay_in_settings = False

        else:
            print("Ups I didn't understand that command. Please try again!")


# Converts Iotas into the unit that is set in the account settings and returns a string
def convert_units(value):
    unit = settings[0]['units']
    value = float(value)

    if unit == "i":
        value = str(int(value)) + "i"
        return value

    elif unit == "ki":
        value = '{0:.3f}'.format(value/1000)
        value = str(value + "Ki")
        return value

    elif unit == "mi":
        value = '{0:.6f}'.format(value / 1000000)
        value = str(value) + "Mi"
        return value

    elif unit == "gi":
        value = '{0:.9f}'.format(value / 1000000000)
        value = str(value + "Gi")
        return value

    elif unit == "ti":
        value = '{0:.12f}'.format(value / 1000000000000)
        value = str(value + "Ti")
        return value


# Takes a address (81 Characters) and converts it to an address with checksum (90 Characters)
def address_checksum(address):
    bytes_address = bytes(address)
    addy = Address(bytes_address)
    address = str(addy.with_valid_checksum())
    return address


# Takes an address with checksum and verifies if the address matches with the checksum
def is_valid_address(address_with_checksum):
    address = address_with_checksum[:81]
    new_address_with_checksum = address_checksum(address)
    if new_address_with_checksum == address_with_checksum:
        return True
    else:
        return False


# Writes the index, address and balance, as well as the checksum of address + seed into the account file
def write_address_data(index, address, balance):
    address = address_checksum(address)
    for p in address_data:
        if p["address"] == address:
            p["balance"] = balance
            with open(file_name, 'w') as account_data:
                json.dump(raw_account_data, account_data)
            return

    checksum = get_checksum(address)
    raw_account_data["account_data"][0]["address_data"].append({
        'index': index,
        'address': address,
        'balance': balance,
        'checksum': checksum
    })

    with open(file_name, 'w') as account_data:
        json.dump(raw_account_data, account_data)


# Takes the f_index and/or the l_index and saves them in the account file
# "f_index" is the index of the first address with balance and "l_index" is the index of the last address with balance
def write_fal_balance(f_index=0, l_index=0):
    if f_index > 0 and l_index > 0:
        fal_balance[0]["f_index"] = f_index
        fal_balance[0]["l_index"] = l_index

    elif f_index > 0:
        fal_balance[0]["f_index"] = f_index
    elif l_index > 0:
        fal_balance[0]["l_index"] = l_index
    else:
        return

    with open(file_name, 'w') as account_data:
        json.dump(raw_account_data, account_data)


# Writes data of an transaction to the account file
def write_transfers_data(
        transaction_hash,
        is_confirmed,
        timestamp,
        tag,
        address,
        message,
        value,
        bundle
):
    for p in transfers_data:
        if p["transaction_hash"] == transaction_hash:
            if is_confirmed == p["is_confirmed"]:
                return
            else:
                p['is_confirmed'] = is_confirmed
                with open(file_name, 'w') as account_data:
                    json.dump(raw_account_data, account_data)
                return

    raw_account_data["account_data"][0]["transfers_data"].append({
        'transaction_hash': transaction_hash,
        'is_confirmed': is_confirmed,
        'timestamp': timestamp,
        'tag': tag,
        'address': address,
        'message': message,
        'value': value,
        'bundle': bundle

    })

    with open(file_name, 'w') as account_data:
        json.dump(raw_account_data, account_data)


# Updates the f_index and l_index
def update_fal_balance():

    index_with_value = []
    for data in address_data:
        if data["balance"] > 0:
            index = data["index"]
            index_with_value.append(index)

    if len(index_with_value) > 0:
        f_index = min(index_with_value)
        l_index = max(index_with_value)
        write_fal_balance(f_index, l_index)

    return


# Sends a request to the IOTA node and gets the current confirmed balance
def address_balance(address):
    api = Iota(iota_node)
    gna_result = api.get_balances([address])
    balance = gna_result['balances']
    return balance[0]


# Checks all addresses that are saved in the account file and updates there balance
# start_index can be set in order to ignore all addresses befor the start index
def update_addresses_balance(start_index=0):
    max_index = 0
    for data in address_data:
        index = data["index"]
        if start_index <= index:
            address = str(data["address"])
            balance = address_balance(address)
            write_address_data(index, address, balance)

        if max_index < index:
            max_index = index

    if max_index < start_index:
        print("Start index was not found. You should generate more addresses or use a lower start index")


# Generates one or more addresses and saves them in the account file
def generate_addresses(count):
        index_list = [-1]
        for data in address_data:
            index = data["index"]
            index_list.append(index)

        if max(index_list) == -1:
            start_index = 0
        else:
            start_index = max(index_list) + 1
        generator = AddressGenerator(seed)
        addresses = generator.get_addresses(start_index, count)  # This is the actual function to generate the address.
        i = 0

        while i < count:
            index = start_index + i
            address = addresses[i]
            balance = address_balance(address)
            write_address_data(index, str(address), balance)
            i += 1

        update_fal_balance()


# Will generate and scan X addresses of an seed for balance. If there are already saved addresses in the ac-
# count data, it will start with the next higher address index
def find_balance(count):
    max_gap = 3
    margin = 4
    i = 0
    balance_found = False
    print("Generating addresses and checking for balance, please wait...\n")
    while i < count and margin > 0:
        print("Checking address " + str(i+1) + " in range of " + str(count))
        generate_addresses(1)
        index_list = []
        for data in address_data:
            index = data['index']
            index_list.append(index)
        max_index = max(index_list)
        for data in address_data:
            index = data['index']
            balance = data['balance']
            if index == max_index and balance > 0:
                balance_found = True
                address = data['address']
                print("Balance found! \n" +
                      "   Index: " + str(index) + "\n" +
                      "   Address: " + str(address) + "\n" +
                      "   Balanc: " + convert_units(balance) + "\n")
                margin = max_gap
                if count - i <= max_gap:
                    count += max_gap

            elif index == max_index and margin <= max_gap:
                margin -= 1

        i += 1
    if not balance_found:
        print("No address with balance found!")


# Gets the first address after the last address with balance. If there is no saved address it will generate a new one
def get_deposit_address():
    try:
        l_index = fal_balance[0]["l_index"]
        if l_index == 0:
            deposit_address = address_data[0]["address"]
            return deposit_address

        for p in address_data:
            address = p["address"]
            checksum = p["checksum"]
            integrity = verify_checksum(checksum, address)
            if p["index"] > l_index and integrity:
                deposit_address = p["address"]
                return deposit_address
            elif not integrity:
                return "Invalid checksum!!!"
        print("Generating address...")
        generate_addresses(1)
        for p in address_data:
            address = p["address"]
            checksum = p["checksum"]
            integrity = verify_checksum(checksum, address)
            if p["index"] > l_index and integrity:
                deposit_address = p["address"]
                return deposit_address
    except:
        "An error acoured while trying to get the deposit address"


# Displays all saved addresses and there balance
def full_account_info():
    update_addresses_balance(fal_balance[0]["f_index"])
    update_fal_balance()
    if len(address_data) > 0:
        all_address_data = ""
        for p in address_data:
            address = p["address"]
            checksum = p["checksum"]
            balance = int(p["balance"])
            integrity = verify_checksum(checksum, address)
            if integrity:
                data = "Index: " + str(p["index"]) + "   " + p["address"] +\
                       "   balance: " + convert_units(balance) + "\n"
                all_address_data += data

            else:
                data = "Index: " + str(p["index"]) + "   Invalid Checksum!!!" + "\n"
                all_address_data += data

        print(all_address_data)
        fal_data = "First index with balance: " + str(
            fal_balance[0]["f_index"]) + "\n" + "Last index with balance is: " + str(fal_balance[0]["l_index"])
        print(fal_data)
    else:
        print("No Data to display!")


# Displays all addresses with balance, the total account balance and a deposit address.
# In case that there are no saved addresses it will ask if the account should be scanned for balance
# If the User answers with no, then it will just generate a deposit address (at index 0)
def standard_account_info():
    address_count = len(address_data)
    update_addresses_balance(fal_balance[0]["f_index"])
    update_fal_balance()

    if address_count < 1:
        print("\n\nThis seems to be the first time you are using this account with the CL wallet!\n"
              "If you are expecting balance on this account you should scan for balance.\n"
              "Do you want to scan for balance?\n\n ")
        yes = yes_no_user_input()
        if yes:
            print("\n\nOkay great, I will generate addresses and check them for balance!\n"
                    "Plese tell me how many addresses I should check. If you say 100\n"
                    "I will generate addresses until balance is found or until 100 addresses\n"
                    "have been generated.\n"
                    "So, whats the maximum number of addresses I should check?\n\n")
            prompt = "Please enter the max number of addresses to check: "
            addresses_to_check = numbers_user_input(prompt)
            if addresses_to_check > 0:
                find_balance(addresses_to_check)
                standard_account_info()

            elif addresses_to_check == 0:
                print("You entered 0! I won't check any addresses.")
        elif not yes:
            print("\nOkay, then I will just generate a deposit address.\n"
                  "In case you wan't to generate addresses after that, you can use the \"find balance\" command.\n"
                  "Generating deposit address...\n\n\n")
            generate_addresses(1)
            standard_account_info()
            return

    elif address_count > 0:
        all_address_data = ""
        total_balance = 0
        for p in address_data:
            balance = p["balance"]
            address = p["address"]
            checksum = p["checksum"]
            integrity = verify_checksum(checksum, address)
            if balance > 0 and integrity:
                total_balance += balance
                data = "Index: " + str(p["index"]) + "   " + address + "   balance: " + convert_units(balance) + "\n"
                all_address_data += data

            elif not integrity:
                total_balance += balance
                data = "Index: " + str(p["index"]) + "   Invalid Checksum!!!" + "\n"
                all_address_data += data

        if total_balance > 0:
            print(all_address_data)
            print("\n" + "Deposit address: " + str(get_deposit_address()))
            print("\nTotal Balance: " + convert_units(total_balance))

        else:
            print("No addresses with balance!")
            print("\n" + "Deposit address: " + str(get_deposit_address()))


# Will ask the user to enter the amount and Units (Iota, MegaIota, GigaIota,etc.)
def transfer_value_user_input():
    print("\n\nEnter a number and the the unit size.\n"
          "Avaliable units are \"i\"(Iota), \"ki\"(KiloIota), \"mi\"(MegaIota), "
          "\"gi\"(GigaIota) and \"ti\"(TerraIota)\n"
          "Example: If you enter \"12.3 gi\", I will send 12.3 GigaIota\n")
    ask_user = True
    while ask_user:
        user_input = raw_input("Please enter the amount to send: ")
        user_input = user_input.upper()
        user_input_as_list = list(user_input)

        allowed_characters = list("1234567890. IKMGT")
        allowed_for_numbers = list("1234567890.")
        allowed_for_units = list("iIkKmMgGtT")
        is_valid = True

        value = ""
        unit = ""
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

                if unit == "I":
                    value = value
                    if 1 > value > 0:
                        print("You entered a amount greater then 0 but smaller then 1 Iota!\n"
                              "Can only send whole Iotas...\n ")
                    else:
                        return int(value)

                elif unit == "KI":
                    value *= 1000
                    if 1 > value > 0:
                        print("You entered a amount greater then 0 but smaller then 1 Iota!\n"
                              "Can only send whole Iotas...\n ")
                    else:
                        return int(value)

                elif unit == "MI":
                    value *= 1000000
                    if 1 > value > 0:
                        print("You entered a amount greater then 0 but smaller then 1 Iota!\n"
                              "Can only send whole Iotas...\n ")
                    else:
                        return int(value)

                elif unit == "GI":
                    value *= 1000000000
                    if 1 > value > 0:
                        print("You entered a amount greater then 0 but smaller then 1 Iota!\n"
                              "Can only send whole Iotas...\n ")
                    else:
                        return int(value)

                elif unit == "TI":
                    value *= 1000000000000
                    if 1 > value > 0:
                        print("You entered a amount greater then 0 but smaller then 1 Iota!\n"
                              "Can only send whole Iotas...\n ")
                    else:
                        return int(value)
                else:
                    print("You didn't enter a valid unit size! Please try again\n")

            except:
                print("You didn't enter a valid value! Please try again\n")

        else:
            print("You didn't enter a valid value! Please try again\n")


# Gets all necessary data from the user to make one or more transfers
def prepare_transferes():
    new_transfer = True
    prepared_transferes = []
    while new_transfer:
        get_recipient_address = True
        while get_recipient_address:
            recipient_address = raw_input("\nPlease enter the receiving address: ")

            if len(recipient_address) == 81:
                print("You enterd a address without checksum. Are you sure you want to continiue?")
                yes = yes_no_user_input()
                if yes:
                    get_recipient_address = False
                else:
                    print("Good choice! Addresses with checksum are a lot safer to use.")
            elif len(recipient_address) == 90:
                is_valid = is_valid_address(recipient_address)
                if is_valid:
                    get_recipient_address = False
                else:
                    print("Invalid address!! Please try again!")
            else:
                print("\nYou enterd a invalid address. Address must be 81 or 90 Char long!")

        recipient_address = bytes(recipient_address)
        user_message = raw_input("Please enter a message: ")
        user_tag = raw_input("Please enter a tag: ")
        user_tag = bytes(user_tag)
        transfer_value = transfer_value_user_input()
        txn = \
            ProposedTransaction(
                address=Address(
                    recipient_address
                ),

                message=TryteString.from_string(user_message),
                tag=Tag(user_tag),
                value=transfer_value,
            )
        prepared_transferes.append(txn)
        print("Do you want to prepare another transfer?")
        yes = yes_no_user_input()
        if not yes:
            new_transfer = False

    review_transfers(prepared_transferes)


# Before a transfer is actually sent, it will be displayed and can be canceled or confirmed by the user
def review_transfers(prepared_transferes):
    transfers_to_print = ""

    for txn in prepared_transferes:
        address = str(txn.address)
        value = str(convert_units(int(txn.value)))
        line = "------------------------------------------------" \
               "--------------------------------------------------------------\n"
        transfers_to_print += address + "  |  " + value + "\n" + line
    print("\n\n\nDestination:                                  "
          "                                              |  Value:\n"
          "-----------------------------------------------------"
          "---------------------------------------------------------")
    print(transfers_to_print)
    print("\n\nPlease review the transfer(s) carefully!\n")

    ask_user = True
    while ask_user:
        user_input = raw_input("\nEnter \"confirm\" to send the transfer(s)\n"
                               "Enter \"cancel\" to cancel the transfer(s)")
        user_input = user_input.upper()

        if user_input == "CONFIRM":
            print("\n\nOkay, sending transfer(s) now. This can take a while...")
            ask_user = False
            try:
                send_transfer(prepared_transferes)
            except:
                print("A error occurred :(")

        elif user_input == "CANCEL":
            print("\n\nTransfer(s) canceled!")
            ask_user = False

        else:
            print("Ups, I didn't understand that. Please try again!")


# Takes the prepared transaction data and sends it to the IOTA node for attaching itto the tangle
def send_transfer(prepared_transferes):
    print("Sending transfer, this can take a while...")
    change_addy = bytes(get_deposit_address())
    api = Iota(iota_node, seed)
    api.send_transfer(
        depth=7,
        transfers=prepared_transferes,
        change_address=change_addy,
        min_weight_magnitude=18
        )
    print("Transaction compleated!")


# Not yet implemented
def replay_transaction():
    pass


# -------------------------------------Transaction history------------------------------------------------------------


# Reads the data from the account file and displays it to the user.
# If full_history is True it will print all transactions that are saved.
# If full_history is false it will print only confirmed transactions unless the transaction is no older then
# 6 hours, then it will print the transaction regardless of it's confirmation state
def print_transaction_history(full_history=False):
    current_unix_time = time.time()
    sorted_transactions = sorted(transfers_data, key=itemgetter('timestamp'))  # Sort the transactions by timestamp
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
        elif is_confirmed == "True":
            address = address_checksum(str(addy['address']))
            addresses_with_confirmed_transactions.append(address)

    addresses_with_confirmed_transactions = set(addresses_with_confirmed_transactions)
    addresses_with_confirmed_transactions = list(addresses_with_confirmed_transactions)
    addresses_with_new_transactions = set(addresses_with_new_transactions)
    addresses_with_new_transactions = list(addresses_with_new_transactions)

    for transaction in sorted_transactions:
        timestamp = int(transaction['timestamp'])
        txn_time = datetime.datetime.fromtimestamp(
            int(timestamp)
        ).strftime('%Y-%m-%d %H:%M:%S')
        is_confirmed = str(transaction['is_confirmed'])
        transaction_hash = transaction['transaction_hash']
        address = address_checksum(str(transaction['address']))
        bundle = transaction['bundle']
        tag = transaction['tag']
        value = transaction['value']

        if full_history:
            data = {'txn_time': str(txn_time), 'address': str(address), 'transaction_hash': str(transaction_hash),
                    'value': str(value), 'tag': str(tag), 'bundle': str(bundle), 'is_confirmed': str(is_confirmed)}
            all_transactions.append(data)

        elif current_unix_time - timestamp < 25200:
            data = {'txn_time': str(txn_time), 'address': str(address), 'transaction_hash': str(transaction_hash),
                    'value': str(value), 'tag': str(tag),  'bundle': str(bundle), 'is_confirmed': str(is_confirmed)}
            new_transactions.append(data)

        elif is_confirmed == "True":
            data = {'txn_time': str(txn_time), 'transaction_hash': str(transaction_hash),
                    'address': str(address), 'value': str(value), 'bundle': str(bundle), 'tag': str(tag)}
            old_confirmed_transactions.append(data)

    if len(new_transactions) > 0 and not full_history:
        print("\n\n\n                                                New Transactions")
        print("--------------------------------------------------------------------------------------------------------"
              "---------")
        for addy in addresses_with_new_transactions:
            addy = address_checksum(str(addy))
            print("\nTransactions to/from: " + str(addy) + "\n")
            for data in new_transactions:
                    address = data['address']
                    if address == addy:
                        txn_time = data['txn_time']
                        transaction_hash = data['transaction_hash']
                        value = data['value']
                        bundle = data['bundle']
                        tag = data['tag']
                        is_confirmed = data['is_confirmed']
                        print(" " + txn_time + "\n" +
                              "    Txn Hash: " + transaction_hash + "  " + str(convert_units(value)) + "\n" +
                              "    Bundle: " + bundle + "\n" +
                              "    Tag: " + tag + "\n" +
                              "    Confirmed: " + is_confirmed + "\n")

    if len(old_confirmed_transactions) > 0 and not full_history:
        print("\n\n\n                                                 Old Confirmed Transactions")
        print("--------------------------------------------------------------------------------------------------------"
              "---------")
        for addy in addresses_with_confirmed_transactions:
            addy = address_checksum(str(addy))
            print("\nTransactions to/from: " + str(addy) + "\n")

            for data in old_confirmed_transactions:
                    address = data['address']
                    if address == addy:
                        txn_time = data['txn_time']
                        transaction_hash = data['transaction_hash']
                        value = data['value']
                        bundle = data['bundle']
                        tag = data['tag']
                        print(" " + txn_time + "\n" +
                              "    Txn Hash: " + transaction_hash + "  " + str(convert_units(value)) + "\n" +
                              "    Bundle: " + bundle + "\n" +
                              "    Tag: " + tag + "\n")

    if len(new_transactions) == 0 and len(old_confirmed_transactions) == 0 and len(all_transactions) == 0:
        print("No transactions in history!")

    elif full_history:
        print("\n\n\n                                                 Full transaction history")
        print("--------------------------------------------------------------------------------------------------------"
              "---------\n\n")
        for data in all_transactions:
            address = data['address']
            txn_time = data['txn_time']
            transaction_hash = data['transaction_hash']
            value = data['value']
            bundle = data['bundle']
            tag = data['tag']
            is_confirmed = data['is_confirmed']
            print(" " + txn_time + "\n" +
                  " To/From: " + address + "\n"
                  "          Txn Hash: " + transaction_hash + "  " + str(convert_units(value)) + "\n" +
                  "          Bundle: " + bundle + "\n" +
                  "          Tag: " + tag + "\n" +
                  "          Confirmed: " + is_confirmed + "\n")


# Gets all assosiated transactions from the saved addresses and saves the transaction data in the account file
def get_transfers(full_history):
    api = Iota(iota_node, seed)
    address_count = len(address_data)
    all_txn_hashes = []
    saved_txn_hashes = []
    new_txn_hashes = []
    i = 0

    while i < address_count:
        address = address_data[i]["address"]
        address_as_bytes = [bytes(address)]
        raw_transfers = api.find_transactions(addresses=address_as_bytes)
        transactions_to_check = raw_transfers["hashes"]

        for txn_hash in transactions_to_check:
            txn_hash = str(txn_hash)
            all_txn_hashes.append(txn_hash)
        i += 1

    for txn_hash in transfers_data:
        txn_hash = str(txn_hash['transaction_hash'])
        saved_txn_hashes.append(txn_hash)

    for txn_hash in all_txn_hashes:
        if txn_hash not in saved_txn_hashes:
            new_txn_hashes.append(txn_hash)

    if len(new_txn_hashes) > 0:
        print("Retreaving and saving transfer data from " + str(len(new_txn_hashes)) + " transaction(s)!\n"
              "Please wait...\n")
        for txn_hash in new_txn_hashes:
            txn_hash_as_bytes = bytes(txn_hash)
            li_result = api.get_latest_inclusion([txn_hash_as_bytes]) # Needs to be integrated into new transactions as well
            is_confirmed = li_result['states'][txn_hash]

            gt_result = api.get_trytes([txn_hash_as_bytes])
            trytes = str(gt_result['trytes'][0])
            txn = Transaction.from_tryte_string(trytes)
            timestamp = str(txn.timestamp)
            tag = str(txn.tag)
            address = str(txn.address)
            message = "some message"  # Placeholder untill message decoding is added
            value = str(txn.value)
            bundle = str(txn.bundle_hash)

            write_transfers_data(
                txn_hash,
                is_confirmed,
                timestamp,
                tag,
                address,
                message,
                value,
                bundle
            )

    if full_history:
        print_transaction_history(full_history)

    elif not full_history:
        print_transaction_history(full_history)


# The function that rules them all!
# This function will be called when the script is executed and will ask the user for the seed and then listens to
# the users commands. All functions above will be called directly or indirectly through this function.
def main():
    ask_seed = True
    while ask_seed:
        global seed
        global file_name
        seed = log_in()
        file_name = create_file_name()

        global raw_account_data
        global settings
        global address_data
        global fal_balance
        global transfers_data

        raw_account_data = read_account_data()
        settings = raw_account_data['account_data'][0]['settings']
        address_data = raw_account_data['account_data'][0]['address_data']
        fal_balance = raw_account_data['account_data'][0]['fal_balance']
        transfers_data = raw_account_data['account_data'][0]['transfers_data']

        global iota_node
        iota_node = settings[0]['host']

        logged_in = True

        while logged_in:

            user_command_input = raw_input("\n \nPlease enter a command."
                                           " Type \"HELP\" to see all avaliable commands:  ")
            print("\n")

            if user_command_input == "account info":
                standard_account_info()

            elif user_command_input == "full account info":
                full_account_info()

            elif user_command_input == "find balance":
                print("How many addresses should be checked?\n"
                      "If I find a address with balance and the following three addresses\n"
                      "don't have any balance, I will stop searching.\n")
                prompt = "So, what is the maximum number of addresses I should check?"
                number = numbers_user_input(prompt)
                find_balance(number)

            elif user_command_input == "generate new address":
                print("Generating 1 address...")
                generate_addresses(1)

            elif user_command_input == "send transfer":
                prepare_transferes()

            elif user_command_input == "account history":
                get_transfers(full_history=False)

            elif user_command_input == "full account history":
                get_transfers(full_history=True)

            elif user_command_input == "settings":
                set_settings()

            elif user_command_input == "exit":
                print("See you!\n\n\n")
                return

            elif user_command_input == "log out":
                print("Logging out...\n\n\n")
                logged_in = False

            elif user_command_input == "HELP":
                print("""Avaliable commands:

        "account info"
            Will show you each address containing balance, total balance and your deposit address.

        "full account info"
            Will show you all saved addresses and there corespoding balance.

        "find balance"
            Searches for the first address with balance within a user defined range(e.g. first 100 addresses)

        "generate new address"
            Generates one new addresses!

        "send transfer"
            Send one or more transfers

        "account history"
            Shows all confirmed transfers and all new transfers (from your saved account addreses)


        "full account history"
            Shows all transfers, including old non confirmed transfers (from your saved account addreses)

        "settings"
            Set the minWeightMagnitude and the Units used to display iota tokens (i,Ki,Mi,Gi,Ti)

        "log out"
            Log out of your account and login with a different seed

        "exit"
            Exit the wallet.

                    """)

            else:
                print("Ups I didn't understand that command. Please try again!")


main()
