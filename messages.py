account = dict(
    welcome='\n\nSeems like its your first time logging in to this seed!\n'
            'By default the wallet will connect'
            ' to testnet node http://bahamapascal-tn1.ddns.net:14200'
            '(while in Beta)\n'
            'Do you want to connect to another host?\n\n',
    login_welcome='\n\n\n------------------------------------------------'
        'Account login---------------------------------------'
        '-----------------'
        '\n\nA seed should only contain the letters A-Z and 9.'
        ' Lowercase letters will automatically be converted to\n'
        'uppercase and everything else that is not A-Z,'
        ' will be converted to a 9.',
    enter_seed='\n \nPlease enter your'
                            ' seed to login to your account: ',
    seed_hash='\n\nThe Sha256 hash of your seed is:',
    seed_review='Should the seed be displayed for review?\n',
    entered_seed='You entered ' + "{}" + ' as seed.',
    seed_display_prompt='OK, seed won\'t be displayed!',
    choose_host='\nPlease enter the host'
                ' you want to connect to: '
)

wallet = dict(
    welcome='\nStarting wallet...\n\n\n\n'
)

helpers = dict(

)

settings = dict(
    description_min_weight_magnitude='Enter "min_weight_magnitude" to set the minWeightMagnitude',
    description_units='Enter "unit" to set the Units used'
            ' to display iota tokens (i,Ki,Mi,Gi,Ti)',
    description_host='Enter "host" to set a new host to connect to',
    description_current_settings='Enter "current_settings" to see',
    description_back='Enter "back" to quit the settings menu\n\n',
    command_input='Please enter a command: ',
    enter_min_weight_magnitude='\nPlease enter the minWeightMagnitude: ',
    min_weight_magnitude_set='minWeightMagnitude set to' + "{}" + '\n\n',
    enter_units='\nPlease enter "i","ki","mi","gi" or "ti": ',
    units_set='Units set to ' + "{}" + '\n\n',
    invalid_unit='\n\nUps you seemed to have'
                        ' entered something else'
                        ' then "i","ki","mi","gi" or "ti" ',
    enter_host='\nPlease enter the'
                    ' host you want to connect to: ',
    host_set='Host set to ' + "{}" + '\n\n',
    current_settings='\n\nMinWeightMagnitude is currently set to '
                    + "{}" + '\n' +
                    'Units are set to ' + "{}" + '\n' +
                    'Host is set to ' + "{}" + '\n\n'
)

common = dict(
    try_again='Please try again.',
    invalid_command='Ups I didn\'t understand'
                    ' that command. Please try again!' # TODO: Tweak sentence and wordings to make it more general
)