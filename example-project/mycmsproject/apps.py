from django.apps import AppConfig


class MyCMSProjectConfig(AppConfig):
    name = "mycmsproject"
    verbose_name = "My CMS Project"

    def ready(self):
        """
        Loads the signals for the API
        """
        from mycmsproject import signals

        assert signals
