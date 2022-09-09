import telebot
from django.conf import settings
from account.services.registration import generate_confirm_code
from django.core.cache import cache
from account.models import User


bot = telebot.TeleBot(settings.INFO_BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        User.objects.get(tg_id=message.chat.id)
        # TODO: "вы уже зарегистрировались, используйте команду /login"
        return
    except User.DoesNotExist:
        pass
    cache_code = cache.get(f'login_tg_{message.chat.id}')
    if not cache_code:
        code = generate_confirm_code()
        cache.set(f'register_code_{code}', message.chat.id, settings.USER_CONFIRM_TG_TIMEOUT)
        cache.set(f'register_tg_{message.chat.id}', code, settings.USER_CONFIRM_TG_TIMEOUT)

    else:
        code = cache_code
    msg = settings.CONFIRM_REGISTER_MESSAGE.substitute(code=code)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['login'])
def login(message):
    try:
        User.objects.get(tg_id=message.chat.id)
    except User.DoesNotExist:
        bot.send_message(message.chat.id, 'Сначало пройдите регистрацию на сайте!')
        return

    cache_code = cache.get(f'login_tg_{message.chat.id}')
    if not cache_code:
        code = generate_confirm_code()
        cache.set(f'login_code_{code}', message.chat.id, settings.USER_CONFIRM_TG_TIMEOUT)
        cache.set(f'login_tg_{message.chat.id}', code, settings.USER_CONFIRM_TG_TIMEOUT)
    else:
        code = cache_code
    msg = settings.CONFIRM_LOGIN_MESSAGE.substitute(code=code)
    bot.send_message(message.chat.id, msg)


def run_polling():
    bot.polling(non_stop=True)
