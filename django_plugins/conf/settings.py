from django.conf import settings

PLUGINS_MODULE = getattr(settings, "PLUGINS_MODULE", "plugins")
PLUGINS_AUTO_LOAD = getattr(settings, "PLUGINS_AUTO_LOAD", True)
PLUGINS_AUTO_REMOVE = getattr(settings, "PLUGINS_AUTO_REMOVE", True)
PLUGINS_ALLOW_POINT_SUBLEVELS = getattr(settings, "PLUGINS_ALLOW_POINT_SUBLEVELS", 1)
