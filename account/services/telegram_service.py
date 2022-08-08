import telebot
from django.conf import settings

bot = telebot.TeleBot(settings.INFO_BOT_TOKEN)


def send_message(receiver_id: str, message: str):
    bot.send_message(receiver_id, message)
