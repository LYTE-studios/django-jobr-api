from django.apps import AppConfig


class SuggestionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'suggestions'
    verbose_name = 'AI Suggestions'

    def ready(self):
        try:
            import suggestions.signals  # noqa
        except ImportError:
            pass
