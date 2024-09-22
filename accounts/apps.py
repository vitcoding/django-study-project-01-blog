from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    # for signals of profile creation
    def ready(self):
        import accounts.signals
