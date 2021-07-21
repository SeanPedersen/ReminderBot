# Reminder Telegram Bot
import configparser
import time
import math
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext
)
from telegram.ext.dispatcher import run_async
from persistence import DBConn


def next_rem(current, created, interval):
    return created + math.ceil((current - created) / interval) * interval

def reminder_thread(updater):
    """Sends out reminders when they are due"""
    
    while True:
        unix_current = int(time.time())

        with DBConn() as db:
            reminders = db.get_reminders()
        next_up_reminders = []
        for message, created_time, interval_hours, telegram_id in reminders:
            next_up_reminders.append((telegram_id, message, next_rem(unix_current, created_time, interval_hours * 60 * 60)))
        time.sleep(5)
        print("BEEP, Current:", unix_current)
        unix_current = int(time.time())
        print("Scheduled:", next_up_reminders)
        for telegram_id, message, next_time in next_up_reminders:
            if unix_current > next_time:
                print(unix_current, ">=", next_time, " - LIVE:", message)
                updater.bot.send_message(chat_id=telegram_id, text=message)

def start(update: Update, context: CallbackContext):
    """Start bot"""
    with DBConn() as db:
        name = update.message.from_user.first_name
        try:
            db.add_user(name, update.message.from_user.id)
        except sqlite3.IntegrityError:
            pass # Ignore existing user
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hello {name}, bot started!")

def create_reminder_0(update: Update, context: CallbackContext):
    """Create a new reminder message"""
    context.bot.send_message(chat_id=update.effective_chat.id, text="What shall I remind you of?")
    return 0

def create_reminder_1(update: Update, context: CallbackContext):
    reminder_message = update.message.text
    if reminder_message == "/cancel":
        return cancel(update, context)
    context.chat_data["reminder_message"] = reminder_message
    context.bot.send_message(chat_id=update.effective_chat.id, text="Enter an interval in hours")
    return 1

def create_reminder_2(update: Update, context: CallbackContext):
    reminder_interval = update.message.text
    if reminder_interval == "/cancel":
        return cancel(update, context)
    with DBConn() as db:
        db.add_reminder(update.message.from_user.id, context.chat_data["reminder_message"], reminder_interval)
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
                                    create_reminder_0,
                                    )],
        states={
            0: [
                MessageHandler(Filters.text, create_reminder_1)
            ],
            1: [
                MessageHandler(Filters.text, create_reminder_2)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    DP.add_handler(new_reminder_handler)

    print("Bot is running...")
    DP.run_async(reminder_thread, UPDATER)
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
