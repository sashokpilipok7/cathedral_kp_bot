"""
index.py
---------
index all function handlers
"""


# imports here -----------------------
from telegram import ReplyKeyboardMarkup, KeyboardButton, BotCommand
from .start import start
from .echo import echo
from .help import help_command
from .hello import hello
from .whoami import whoami
from .events import events
from .broadcast import broadcast_test

command_map = {
    'start': start,
    'echo' : echo,
    'whoami' : whoami,
    'hello' : hello,
    'events' : events,
    'help' : help_command,
    'broadcast': broadcast_test
    }

button_map = {
    '🚀 Почати': start,
    '👋 Вітання': hello,
    '📅 Події': events,
    '❓ Допомога': help_command
    }

bot_commands = [
    BotCommand('start', '🚀 Почати'),
    BotCommand('hello', '👋 Вітання'),
    BotCommand('events', '📅 Події'),
    BotCommand('help', '❓ Допомога'),
]

# --------------------------------------
def index():
    """
    
    """
    return command_map

def get_menu_markup():
    keyboard = [
        [KeyboardButton('🚀 Почати'), KeyboardButton('👋 Вітання')],
        [KeyboardButton('📅 Події'), KeyboardButton('❓ Допомога')]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def handle_menu_button(update, context):
    if update.message and update.message.text in button_map:
        return button_map[update.message.text](update, context)