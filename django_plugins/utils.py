from importlib import import_module
from typing import Any

from django.conf import settings
from django.db import connection
from django.urls import include, path


def get_plugin_name(cls):
    """
    Pretty name for a plugin. Includes module and class name.
    """
    return "%s.%s" % (cls.__module__, cls.__name__)


def get_plugin_from_string(plugin_name):
    """
    Returns plugin or plugin point class from given ``plugin_name`` string.

    Example of ``plugin_name``::

        'my_app.MyPlugin'

    """
    modulename, classname = plugin_name.rsplit(".", 1)
    module = import_module(modulename)
    return getattr(module, classname)


def include_plugins(
    point, pattern: str = r"{plugin}/", urls: str = "urls", namespace: Any = None
):
    plugin_urls = []
    for plugin in point.get_plugins():
        if hasattr(plugin, urls) and hasattr(plugin, "name"):
            _urls = getattr(plugin, urls)
            for _url in _urls:
                _url.default_args["plugin"] = plugin.name

            plugin_urls.append(
                path(
                    pattern.format(plugin=plugin.name),
                    include(_urls, namespace=namespace),
                )
            )
    return include(plugin_urls, namespace=namespace)


def import_app(app_name):
    """
    Load the app by its import string.
    Imports are tried in the following order:
    1. import the string as given
    2. else:
        a. extract the last dotted element and try to import an Appconfig from it
        b. if a. succeeded, import the app in app_config.name
    """
    try:
        mod = import_module(app_name)
    except ImportError:  # Maybe it's AppConfig
        parts = app_name.split(".")
        tmp_app, app_cfg_name = ".".join(parts[:-1]), parts[-1]
        try:
            tmp_app = import_module(tmp_app)
        except ImportError:
            raise
        mod = getattr(tmp_app, app_cfg_name).name
        mod = import_module(mod)

    return mod


def load_plugins(plugins_module):
    """
    For all installed apps, load their ``plugins_module`` if it exists.
    """
    for app in settings.INSTALLED_APPS:
        try:
            import_module("%s.%s" % (app, plugins_module))
        except ImportError:
            pass


def db_table_exists(table_name):
    return table_name in connection.introspection.table_names()
