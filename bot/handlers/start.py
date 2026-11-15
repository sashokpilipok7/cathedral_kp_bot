from db import db_manager

def start(update, context):
    """
    /start: 
    Привітання!
    """
    from .index import get_menu_markup
    user = update.effective_user
    db_manager.upsert_user(telegram_id=user.id, username=user.username, first_name=user.first_name,
                           last_name=user.last_name, language_code=user.language_code)
    update.message.reply_text('Слава Ісусу Христу! \n Тисни /events щоб побачити події', reply_markup=get_menu_markup())
