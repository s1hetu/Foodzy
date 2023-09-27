from django.apps import AppConfig


class DeliveryAgentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'delivery_agent'

    def ready(self) -> None:
        from delivery_agent import signals
