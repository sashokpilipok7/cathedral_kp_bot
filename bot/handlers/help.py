from .broadcast import perform_broadcast

def help_command(update, context):
    """
    /help:
    Повертає короткий список команд з інструкціями
    """
    from .index import index, get_menu_markup
    text = '<b>Допомога:</b>\n'
    for k, v in index().items():
        if k != "echo" and k != "whoami":
            text += v.__doc__
    update.message.reply_text(text, parse_mode='HTML', reply_markup=get_menu_markup())

    # FIXME: Schedule broadcast in 10 seconds
    context.job_queue.run_once(perform_broadcast, 10, context=context.bot)
