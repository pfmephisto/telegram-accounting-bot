import os
from dotenv import load_dotenv
from decimal import getcontext, Decimal
from telegram.ext import Updater, CommandHandler, PicklePersistence
import logging


logging.basicConfig(level=logging.INFO)


#  CallbackContext

getcontext().prec = 2

# Load enviroment variables like the bot token
load_dotenv()


def add(update, context):
    """Usage: /add value"""
    # Generate ID and separate value from command
    # We don't use context.args here, because the value may contain whitespaces
    value = update.message.text.partition(' ')[2]
    user_name = update.effective_user.username

    sucsess, value = isDecimal(value)
    response = "Sorry I'm unable to unserstand the value you have assigned"

    if sucsess:
        # Store value
        ledger = get_ledger(context, user_name)

        ledger.append(value)
        set_ledger(context, user_name, ledger)

        response = "I have added {} DKK to your account.\
            \nYour new balance is {} DKK".format(str(value), str(sum(ledger)))

    # Send the key to the user
    update.message.reply_text(response)


def deduct(update, context):
    """Usage: /deduct value"""
    # Generate ID and separate value from command
    # We don't use context.args here, because the value may contain whitespaces
    value = update.message.text.partition(' ')[2]
    user_name = update.effective_user.username

    sucsess, value = isDecimal(value)
    response = "Sorry I'm unable to unserstand the value you have assigned"

    if sucsess:
        # Store value
        value = Decimal.copy_negate(value)
        ledger = get_ledger(context, user_name)
        ledger.append(value)
        set_ledger(context, user_name, ledger)

        response = "I have deducted {} DKK from your account.\
            \nYour new balance is {} DKK".format(str(value), str(sum(ledger)))

    # Send the key to the user
    update.message.reply_text(response)


def list_values(update, context):
    """Usage: /get uuid"""
    # Seperate ID from command
    user_name = update.effective_user.username
    ledger = get_ledger(context, user_name)
    values = "You have no transactions"

    if len(ledger) != 0:
        values = ""
        for val in ledger:
            values = values+"\n{}".format(val)

    response = "Your trasactions are the following:\n{}".format(values)

    update.message.reply_text(response)


def status(update, context):
    if "ledger" in context.chat_data:
        ledger = context.chat_data["ledger"]
        users = [user for user in ledger.keys()]

        response = "This is the ballance of all users in the chat:"

        for user in users:
            value = sum(ledger[user])
            response = response+"\n{name} has {amount}".format(name=user, amount=value)

            update.message.reply_text(response)
    else:
        response = "The have not yet been made any transactions"
        update.message.reply_text(response)


def settle(update, context):
    response = "There was nothing to report"
    if "ledger" in context.chat_data:
        ledger = context.chat_data["ledger"]
        users = [user for user in ledger.keys()]
        if len(users) != 0:
            response = ""
        for user in users:
            value = sum(context.chat_data["ledger"][user])
            response = response+f"{user} has to transefer {value}\n"
        update.message.reply_text(response)

    context.chat_data["ledger"] = dict()
    update.message.reply_text(response)


def isDecimal(value):
    try:
        return (True, Decimal(value))
    except Exception as e:
        logging.info("Error is {}".format(str(e)))
        return (False, Decimal(0))


def get_ledger(context, user_name):
    # ledger_name = ""  # update.message.chat_id
    ledger = []
    if "ledger" in context.chat_data:
        ledger = context.chat_data["ledger"]
        if user_name in ledger:
            ledger = ledger[user_name]
        else:
            ledger = []
    return ledger


def set_ledger(context, user_name, ledger):
    if "ledger" in context.chat_data:
        context.chat_data["ledger"][user_name] = ledger

    else:
        context.chat_data['ledger'] = {user_name: ledger}
    return True


if __name__ == '__main__':

    # Refference to persistant file
    # ../config/data
    my_persistence = PicklePersistence(filename='./config/data')

    updater = Updater(
                      os.getenv("BOT_TOKEN"),
                      persistence=my_persistence,
                      use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('add', add))
    dp.add_handler(CommandHandler('deduct', deduct))
    dp.add_handler(CommandHandler('list', list_values))
    dp.add_handler(CommandHandler('status', status))
    dp.add_handler(CommandHandler('settle', settle))

    updater.start_polling()
    updater.idle()
