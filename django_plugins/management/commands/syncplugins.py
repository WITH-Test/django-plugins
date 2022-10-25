from django.core.management.base import BaseCommand

from django_plugins.conf import settings
from django_plugins.models import ENABLED, REMOVED, Plugin, PluginPoint
from django_plugins.point import PluginMount
from django_plugins.utils import db_table_exists, get_plugin_name, load_plugins


class Command(BaseCommand):
    help = "Syncs the registered plugins and plugin points with the model versions."
    requires_model_validation = True

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            dest="delete",
            help="delete the REMOVED Plugin and PluginPoint instances. ",
        )
        parser.add_argument(
            "--module",
            default=settings.PLUGINS_MODULE,
            dest="module",
            help="find and load this module within applications",
        )

    def handle(self, *args, **options):
        sync = SyncPlugins(
            options.get("module"), options.get("delete"), options.get("verbosity")
        )
        sync.all()


class SyncPlugins:
    """
    In most methods ``src`` and ``dst`` variables are used, their meaning is:

    ``src``
        source, registered plugin point objects

    ``dst``
        destination, database
    """

    def __init__(
        self,
        plugins_module: str,
        delete_removed: bool = False,
        verbosity: int = 1,
    ):
        load_plugins(plugins_module)
        self.delete_removed = delete_removed
        self.verbosity = int(verbosity)

    def print_(self, verbosity, message):
        if self.verbosity >= verbosity:
            print(message)

    def get_classes_dict(self, classes):
        return dict([(get_plugin_name(i), i) for i in classes])

    def get_instances_dict(self, qs):
        return dict((i.import_string, i) for i in qs)

    def available(self, src, dst, model):
        """
        Iterate over all registered plugins or plugin points and prepare to add
        them to database.
        """
        for name, point in src.items():
            inst = dst.pop(name, None)
            if inst is None:
                inst = model.objects.filter(import_string=name).first() or None
            if inst is None:
                self.print_(1, "Registering %s for %s" % (model.__name__, name))
                inst = model(import_string=name)
            if inst.status == REMOVED:
                self.print_(1, "Updating %s for %s" % (model.__name__, name))
                # re-enable a previously removed plugin point and its plugins
                inst.status = ENABLED
            yield point, inst

    def missing(self, dst):
        """
        Mark all missing plugins, that exists in database, but are not
        registered.
        """
        for inst in dst.values():
            if inst.status != REMOVED:
                inst.status = REMOVED
                inst.save()

    def delete(self, dst):
        count = dst.objects.filter(status=REMOVED).count()
        if count:
            self.print_(1, "Deleting %d Removed %ss" % (count, dst.__name__))
            dst.objects.filter(status=REMOVED).delete()

    def points(self):
        src = self.get_classes_dict(PluginMount.points)
        dst = self.get_instances_dict(PluginPoint.objects.all())

        for point, inst in self.available(src, dst, PluginPoint):
            if hasattr(point, "_title"):
                inst.title = point._title
            else:
                inst.title = inst.import_string.split(".")[-1]
            inst.save()
            self.plugins(point, inst)

        self.missing(dst)

        if self.delete_removed:
            self.delete(PluginPoint)

    def plugins(self, point, point_inst):
        src = self.get_classes_dict(point.plugins)
        dst = self.get_instances_dict(point_inst.plugin_set.all())

        for plugin, inst in self.available(src, dst, Plugin):
            inst.point = point_inst
            inst.name = getattr(plugin, "name", None)
            if hasattr(plugin, "title"):
                inst.title = str(getattr(plugin, "title"))
            inst.save()

        self.missing(dst)

    def all(self):
        """
        Synchronize all registered plugins and plugin points to database.
        """
        if not db_table_exists(Plugin._meta.db_table) or not db_table_exists(
            PluginPoint._meta.db_table
        ):
            return
        self.points()
