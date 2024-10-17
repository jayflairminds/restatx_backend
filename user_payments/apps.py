from django.apps import AppConfig


class UserPaymentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user_payments"
    label = "user_payments"
    def ready(self):
        from user_payments import scheduler
        scheduler.start()