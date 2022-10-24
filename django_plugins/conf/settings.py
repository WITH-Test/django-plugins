from django.conf import settings

PLUGINS_MODULE = getattr(settings, "PLUGINS_MODULE", "plugins")
PLUGINS_AUTOLOAD = getattr(settings, "PLUGINS_AUTOLOAD", True)
