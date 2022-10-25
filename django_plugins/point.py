from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from django_plugins.conf import settings

from .models import ENABLED, Plugin
from .models import PluginPoint as PluginPointModel
from .utils import db_table_exists, get_plugin_name

_PLUGIN_POINT = "<class 'django_plugins.point.PluginPoint'>"


def is_plugin_point(cls, gen: int = settings.PLUGINS_ALLOW_POINT_SUBLEVELS):
    """
    Detect a PluginPoint subclass. Disallow more than `gen` levels
    of inheritance.

    Detection is done by checking the repr of the bases because the class
    is needed at its own definition time.

    Parameters
    ----------
    cls
        Class to check.
    gen
        Numbers of generations

    Returns
    -------
        Whether cls is a PluginPoint implementation up to gen levels deep.
    """
    if gen < 1:
        return _PLUGIN_POINT in (repr(base) for base in cls.__bases__)

    # allow n levels of subclassing
    return _PLUGIN_POINT in (repr(base) for base in cls.__bases__[: gen + 1])


class PluginMount(type):
    """
    See: http://martyalchin.com/2008/jan/10/simple-plugin-framework/

    """

    points = []

    def __new__(meta, class_name, bases, class_dict):
        cls = type.__new__(meta, class_name, bases, class_dict)
        if is_plugin_point(cls):
            PluginMount.points.append(cls)
        return cls

    def __init__(cls, name, bases, attrs):
        if is_plugin_point(cls):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
        elif hasattr(cls, "plugins"):
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.plugins.append(cls)

    DoesNotExist = ObjectDoesNotExist


class PluginPoint(metaclass=PluginMount):
    @classmethod
    def get_import_string(cls):
        return get_plugin_name(cls)

    @classmethod
    def is_active(cls):
        if is_plugin_point(cls):
            raise Exception(_("This method is only available to plugin classes."))
        else:
            return cls.get_model().is_active()

    @classmethod
    def get_model(cls, name=None, status=ENABLED):
        """
        Returns model instance of plugin point or plugin, depending on which
        class this method is called.

        Example::

            plugin_model_instance = MyPlugin.get_model()
            plugin_model_instance = MyPluginPoint.get_model('plugin-name')
            plugin_point_model_instance = MyPluginPoint.get_model()

        """
        ppath = cls.get_import_string()
        if is_plugin_point(cls):
            if name is not None:
                kwargs = {}
                if status is not None:
                    kwargs["status"] = status
                return Plugin.objects.get(
                    point__import_string=ppath, name=name, **kwargs
                )
            else:
                return PluginPointModel.objects.get(import_string=ppath)
        else:
            return Plugin.objects.get(import_string=ppath)

    @classmethod
    def get_plugin(cls, name=None, status=ENABLED):
        return cls.get_model(name, status).get_plugin()

    @classmethod
    def get_point(cls):
        """
        Returns plugin point model instance. Only used from plugin classes.
        """
        if is_plugin_point(cls):
            raise Exception(_("This method is only available to plugin classes."))
        else:
            return cls.__base__

    @classmethod
    def get_point_model(cls):
        """
        Returns plugin point model instance. Only used from plugin classes.
        """
        if is_plugin_point(cls):
            raise Exception(_("This method is only available to plugin classes."))
        else:
            return PluginPointModel.objects.get(
                plugin__import_string=cls.get_import_string()
            )

    @classmethod
    def get_plugins(cls, status=ENABLED):
        """
        Returns all plugin instances of plugin point, passing all args and
        kwargs to plugin constructor.
        """
        if not db_table_exists(Plugin._meta.db_table):
            return

        if is_plugin_point(cls):
            for plugin_model in cls.get_plugins_qs(status=status):
                yield plugin_model.get_plugin()
        else:
            raise Exception(_("This method is only available to plugin point classes."))

    @classmethod
    def get_plugins_qs(cls, status=ENABLED):
        """
        Returns query set of all plugins belonging to plugin point.

        Example::

            for plugin_instance in MyPluginPoint.get_plugins_qs():
                print(plugin_instance.get_plugin().name)

        """
        if is_plugin_point(cls):
            point_import_string = cls.get_import_string()
            return Plugin.objects.filter(
                point__import_string=point_import_string, status=status
            ).order_by("index")
        else:
            raise Exception(_("This method is only available to plugin point classes."))

    @classmethod
    def get_name(cls):
        if is_plugin_point(cls):
            raise Exception(_("This method is only available to plugin classes."))
        else:
            return cls.get_model().name

    @classmethod
    def get_title(cls):
        if is_plugin_point(cls):
            raise Exception(_("This method is only available to plugin classes."))
        else:
            return cls.get_model().title
