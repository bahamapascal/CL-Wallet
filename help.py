from terminaltables import SingleTable
from helpers import pretty_print
from messages import help as console_messages


class Help:
    """
    Class for managing "help" command.
    """
    def __init__(self):
        self.table_title = 'Help Section'
        self.table_data = (
            ('Command', 'Description'),
            (console_messages['account_info']['command'], console_messages['account_info']['description']),
            (console_messages['full_account_info']['command'], console_messages['full_account_info']['description']),
            (console_messages['find_balance']['command'], console_messages['find_balance']['description']),
            (console_messages['generate_new_address']['command'], console_messages['generate_new_address']['description']),
            (console_messages['send_transfer']['command'], console_messages['send_transfer']['description']),
            (console_messages['account_history']['command'], console_messages['account_history']['description']),
            (console_messages['full_account_history']['command'], console_messages['full_account_history']['description']),
            (console_messages['replay_bundle']['command'], console_messages['replay_bundle']['description']),
            (console_messages['promote']['command'], console_messages['promote']['description']),
            (console_messages['settings']['command'], console_messages['settings']['description']),
            (console_messages['log_out']['command'], console_messages['log_out']['description']),
            (console_messages['exit']['command'], console_messages['exit']['description']),
        )

        self.print_content()

    def print_content(self):
        """
        Prints help section content to console.

        :return:
          None
        """

        table_instance = SingleTable(self.table_data, self.table_title)
        table_instance.inner_row_border = True

        pretty_print(table_instance.table, color='green')
