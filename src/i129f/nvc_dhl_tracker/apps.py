from django.apps import AppConfig


class I129FConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "i129f.nvc_dhl_tracker"

    def ready(self):
        __import__(f"{self.name}.signals.sender")
        __import__(f"{self.name}.signals.receiver")
