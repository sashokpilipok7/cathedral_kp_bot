def start(update, context):
    """
    /start: 
    Привітання!
    """
    from .index import get_menu_markup
    update.message.reply_text('Слава Ісусу Христу!', reply_markup=get_menu_markup())