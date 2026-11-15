from telegram.error import Unauthorized
from db import db_manager

def perform_broadcast(context):
    """Core logic to send test message to all active users."""
    job = context.job
    bot = context.bot

    users = db_manager.get_active_users()
    count = 0
    failed = 0
    for user in users:
        try:
            bot.send_message(chat_id=user.telegram_id, text="Test message")
            count += 1
        except Unauthorized:
            # The user blocked the bot, mark as inactive
            db_manager.set_user_active(user.telegram_id, False)
            failed += 1
        except Exception as e:
            print(f"Failed to send to {user.telegram_id}: {e}")
            failed += 1
    return count, failed

def broadcast_test(update, context):
    """
    /broadcast:
    Sends a test message to all active users.
    """
    count, failed = perform_broadcast(context.bot)
    update.message.reply_text(f"Successfully sent to {count} users. Failed/Blocked: {failed}.")
