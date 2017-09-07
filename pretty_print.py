from colorama import init, deinit, Fore, Style

colors = dict(
    yellow=Fore.YELLOW,
    blue=Fore.BLUE,
    green=Fore.GREEN,
    red=Fore.RED
)


class PrettyPrint:
    def __init__(self, text, *args, **kwargs):
        init(autoreset=True)  # Initialize colorama
        self.print_text(text, *args, **kwargs)

    def print_text(self, text, color=Fore.YELLOW, style=Style.BRIGHT):
        print(color + style + text)
