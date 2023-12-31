import os

import telebot


bot = telebot.TeleBot("6266133436:AAEJa4yoCblgylIhsyYozyxdv5LLcHyRa20")
chat_id = -1002109047403


def send_message(message):
    bot.send_message(chat_id, message)