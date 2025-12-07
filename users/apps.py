
from django.apps import AppConfig
from django.conf import settings

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        if settings.DEBUG:  # فقط در محیط توسعه
            from django.contrib.sessions.models import Session
            Session.objects.all().delete()  # پاک کردن session ها

