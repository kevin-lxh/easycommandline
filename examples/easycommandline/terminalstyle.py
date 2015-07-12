
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
PURPLE = '\033[95m'
END = '\033[0m'
BOLD = "\033[1m"

def red(text):
    return RED + text + END

def blue(text):
    return BLUE + text + END

def bold(text):
    return BOLD + text + END