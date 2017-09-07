from colorama import init, deinit, Fore, Style

colors = dict(
    yellow=Fore.YELLOW,
    blue=Fore.BLUE,
    green=Fore.GREEN
)


class PrettyPrint:
    def __init__(self, text, *args, **kwargs):
        init()  # Initialize colorama
        self.print_text(text, *args, **kwargs)

    def print_text(self, text, color=Fore.BLUE, style=Style.BRIGHT):
        print(color + style + text)

    def __del__(self):
        deinit()

