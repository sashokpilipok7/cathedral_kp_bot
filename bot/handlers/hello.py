def hello(update, context):
    """
    /hello
    Просто привітайся та отримай відповідь
    """
    from .index import get_menu_markup
    update.message.reply_text(
        'Слава Ісусу Христу! {}, Як ти?'.format(update.message.from_user.first_name),
        reply_markup=get_menu_markup())
