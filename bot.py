# Reminder Telegram Bot
import configparser
import sqlite3
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from persistence import DBConn


def reminder_thread():
    """Sends out reminders when they are due
    Refs:
    - https://stackoverflow.com/questions/47540483/how-to-work-with-simultaneity-with-telegram-bot-python
    - https://github.com/python-telegram-bot/python-telegram-bot/wiki/Performance-Optimizations
    """
    pass

def start(update: Update, context: CallbackContext):
    """Start bot"""
    with DBConn() as db:
        name = update.message.from_user.first_name
        try:
            db.add_user(name, update.message.from_user.id)
        except sqlite3.IntegrityError:
            pass # Ignore existing user
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hello {name}, bot started!")

def create_reminder(update: Update, context: CallbackContext):
    """Create a new reminder message"""
    context.bot.send_message(chat_id=update.effective_chat.id, text="What shall I remind you of?")
    return 0

def create_reminder_2(update: Update, context: CallbackContext):
    reminder_message = update.message.text
    if reminder_message == "/cancel":
        return cancel(update, context)
    with DBConn() as db:
        db.add_reminder(update.message.from_user.id, reminder_message, 1)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Created your reminder!")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Operation canceled.")
    return ConversationHandler.END

def delete_reminder(update: Update, context: CallbackContext):
    """Delete an existing reminder message"""
    context.bot.send_message(chat_id=update.effective_chat.id, text="What is it you had enough of?")


def main():
    print("Server starting...")

    # Create the EventHandler and pass it your bot token
    UPDATER = Updater(CONFIG["KEYS"]["bot"])

    # Get the dispatcher to register handlers
    DP = UPDATER.dispatcher

    # on different commands - answer in Telegram
    DP.add_handler(CommandHandler("start", start))

    new_reminder_handler = ConversationHandler(
        entry_points=[CommandHandler(
                                    "reminder",
                                    create_reminder,
                                    )],
        states={
            0: [
                MessageHandler(Filters.text, create_reminder_2)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    DP.add_handler(new_reminder_handler)

    print("Bot is running...")
    # Start the Bot
    UPDATER.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    UPDATER.idle()


if __name__ == "__main__":
    CONFIG = configparser.ConfigParser()
    CONFIG.read("bot.ini")
    main()
