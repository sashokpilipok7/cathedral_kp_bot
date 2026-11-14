
## handlers
* this folder serves as the placeholder for all function handlers:
handlers
|___ ...
|___ index.py
|___ ...
|___ start.py
|___  echo.py

## index.py
* this file registers all command handler inside this directory, and maps the command handlers name to each function:
command_map = {
    'start': start,
    'echo' : echo }

## handlers/events.py
* Main handler and pert of functionality

## db
* Future main folder for all db process
* db/main.py - for initiate db and create session
* db/models.py for main models like wp_telegram_users, wp_telegram_sent_reminders
