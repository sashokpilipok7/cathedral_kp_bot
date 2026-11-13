from handlers.index import index, handle_menu_button, bot_commands
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from configuration import Config

config = Config('configuration.yaml')
config.show_label()

def main():
    
    updater = Updater(config.token)
    updater.bot.set_my_commands(bot_commands)
    dp = updater.dispatcher
    for k,v in index().items():
        dp.add_handler(CommandHandler(k, v))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_menu_button))
    updater.start_polling()
    updater.idle()

main()