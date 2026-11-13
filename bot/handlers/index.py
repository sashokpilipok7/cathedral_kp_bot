"""
index.py
---------
index all function handlers
"""


# imports here -----------------------
from .start import start
from .echo import echo
from .help import help_command
from .hello import hello
from .whoami import whoami
from .events import events

command_map = {
    'start': start,
    'echo' : echo,
    # ....
    # one-to-one correspondence mapping 
    # map command to function here
    # ....
    'whoami' : whoami,
    'hello' : hello,
    'events' : events,
    'help' : help_command
    }

# --------------------------------------
def index():
    """
    
    """
    return command_map