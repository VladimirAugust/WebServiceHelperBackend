import telebot
from django.conf import settings
from django.db.models import QuerySet

bot = telebot.TeleBot(settings.INFO_BOT_TOKEN)


def send_message(receiver_id: str, message: str, **kwargs):
    bot.send_message(receiver_id, message, **kwargs)

# telebot.apihelper.ApiTelegramException

def multiple_send_msg(recipients_list, message, **kwargs):
    if isinstance(recipients_list, QuerySet):
        recipients_list = [x.tg_id for x in recipients_list]
    for recipient in recipients_list:
        bot.send_message(recipient, message, **kwargs)
