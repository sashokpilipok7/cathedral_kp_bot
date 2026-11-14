import html

def whoami(update, context):
    """
    /whoami: 
    who am i?
    """
    user = update.message.from_user
    first_name = user.first_name
    last_name = user.last_name
    username = user.username

    name = "<b>"+ html.escape(first_name) +"</b>"
    if last_name:
        name += " <b>"+ html.escape(last_name) + "</b>"
    if username:
        name += "\n🤗 @"+ html.escape(username)

    text = "You are:\n👤 {}\n🆔 {}".format(name, str(user.id))

    if 'group' in update.message.chat.type:
        text += "\n👥 " + html.escape(update.message.chat.title)

    update.message.reply_text(text, parse_mode='HTML')