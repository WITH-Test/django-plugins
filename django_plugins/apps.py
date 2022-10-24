from django.apps import AppConfig

from django_plugins.conf import settings
from django_plugins.utils import load_plugins


class DjangoPluginsConfig(AppConfig):
    name = "django_plugins"
    verbose_name = "Django Plugins"

    def ready(self):
        if settings.PLUGINS_AUTOLOAD:
            load_plugins(settings.PLUGINS_MODULE)
