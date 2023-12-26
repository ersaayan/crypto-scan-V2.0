import os

import telebot


bot = telebot.TeleBot("6266133436:AAEJa4yoCblgylIhsyYozyxdv5LLcHyRa20")
chat_id = -949857816


def send_message(message):
    bot.send_message(chat_id, message)