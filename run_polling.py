import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()


from tgbot.main import run_polling


if __name__ == "__main__":
    run_polling()
